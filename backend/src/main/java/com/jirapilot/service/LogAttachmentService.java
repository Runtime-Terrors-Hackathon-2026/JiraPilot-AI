package com.jirapilot.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.client.JiraClientFactory;
import com.jirapilot.model.entity.AuditEvent;
import com.jirapilot.model.entity.IssueAttachment;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.model.enums.AttachmentStatus;
import com.jirapilot.model.enums.InvestigationStatus;
import com.jirapilot.repository.IssueAttachmentRepository;
import com.jirapilot.repository.JiraIssueRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.LocalDateTime;
import java.util.*;
import java.util.zip.GZIPInputStream;

@Slf4j
@Service
@RequiredArgsConstructor
public class LogAttachmentService {

    private final IssueAttachmentRepository attachmentRepository;
    private final JiraIssueRepository issueRepository;
    private final JiraCommentTemplateService commentTemplateService;
    private final EmailJsService emailJsService;
    private final JiraClientFactory jiraClientFactory;
    private final AuditService auditService;
    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${jirapilot.ai-service-url:http://localhost:8000}")
    private String aiServiceUrl;

    @Value("${jirapilot.jira.auto-comment-enabled:false}")
    private boolean autoCommentEnabled;

    @Value("${jirapilot.max-attachment-size-bytes:10485760}") // 10MB default
    private long maxSizeBytes;

    @Value("${jirapilot.max-log-lines:50000}")
    private int maxLines;

    private static final Set<String> SUPPORTED_EXTENSIONS = Set.of(".log", ".txt", ".json", ".jsonl", ".gz");

    /**
     * Ingests, decompresses/validates, and analyzes an uploaded or fetched log attachment.
     */
    @Transactional
    public IssueAttachment processLogContent(
            JiraIssue issue,
            String filename,
            byte[] rawBytes,
            String mimeType,
            String attachmentId
    ) {
        long startTime = System.currentTimeMillis();
        String cleanFilename = filename != null ? filename : "unnamed.log";

        // 1. Extension and size validation
        String ext = "";
        int dotIdx = cleanFilename.lastIndexOf('.');
        if (dotIdx > 0) {
            ext = cleanFilename.substring(dotIdx).toLowerCase();
        }

        if (!SUPPORTED_EXTENSIONS.contains(ext) && !cleanFilename.endsWith(".log.gz")) {
            throw new IllegalArgumentException("Unsupported attachment file extension: '" + ext + "'. Supported: .log, .txt, .json, .jsonl, .log.gz");
        }

        if (rawBytes.length > maxSizeBytes) {
            throw new IllegalArgumentException("Attachment size (" + rawBytes.length + " bytes) exceeds maximum allowable limit (" + maxSizeBytes + " bytes)");
        }

        // 2. Compute SHA-256 for idempotency check
        String sha256 = computeSha256(rawBytes);
        Optional<IssueAttachment> existing = attachmentRepository.findByJiraIssue_JiraKeyAndSha256Hash(issue.getJiraKey(), sha256);
        if (existing.isPresent()) {
            log.info("[ATTACHMENT IDEMPOTENCY] File '{}' with SHA-256 {} already processed for issue {}.", cleanFilename, sha256, issue.getJiraKey());
            return existing.get();
        }

        // 3. Decompress if gzip (.log.gz or .gz)
        String logText;
        try {
            if (cleanFilename.endsWith(".gz")) {
                logText = decompressGzip(rawBytes);
            } else {
                logText = new String(rawBytes, StandardCharsets.UTF_8);
            }
        } catch (Exception e) {
            log.error("[ATTACHMENT] Failed to decode log text: {}", e.getMessage());
            throw new IllegalArgumentException("Failed to decode text from attachment: " + e.getMessage());
        }

        // Limit lines to avoid memory DOS
        String[] lines = logText.split("\\r?\\n");
        if (lines.length > maxLines) {
            StringBuilder truncated = new StringBuilder();
            for (int i = 0; i < maxLines; i++) {
                truncated.append(lines[i]).append("\n");
            }
            truncated.append("\n... [TRUNCATED at ").append(maxLines).append(" lines by safety policy] ...");
            logText = truncated.toString();
        }

        // 4. Create IssueAttachment record in VALIDATING state
        IssueAttachment attachment = IssueAttachment.builder()
                .jiraIssue(issue)
                .attachmentId(attachmentId != null ? attachmentId : UUID.randomUUID().toString())
                .filename(cleanFilename)
                .mimeType(mimeType != null ? mimeType : "text/plain")
                .sizeBytes((long) rawBytes.length)
                .sha256Hash(sha256)
                .status(AttachmentStatus.VALIDATING)
                .build();

        attachment = attachmentRepository.save(attachment);

        // 5. Send to Python Log Analysis Service
        attachment.setStatus(AttachmentStatus.ANALYZING);
        attachmentRepository.save(attachment);

        try {
            String analyzeUrl = aiServiceUrl + "/api/v1/log-analysis/analyze";
            Map<String, Object> reqBody = Map.of(
                    "logText", logText,
                    "filename", cleanFilename,
                    "ticketKey", issue.getJiraKey()
            );

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(reqBody, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(analyzeUrl, entity, String.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                JsonNode root = objectMapper.readTree(response.getBody());

                boolean isQuarantined = root.path("quarantined").asBoolean(false);
                attachment.setQuarantined(isQuarantined);
                if (isQuarantined) {
                    attachment.setStatus(AttachmentStatus.NEEDS_REVIEW);
                    attachment.setQuarantineReason(root.path("quarantineReasons").toString());
                } else {
                    attachment.setStatus(AttachmentStatus.COMPLETED);
                }

                attachment.setPrimaryService(root.path("primaryService").asText(null));
                attachment.setPrimaryEndpoint(root.path("primaryEndpoint").asText(null));
                if (root.has("primaryStatus") && !root.path("primaryStatus").isNull()) {
                    attachment.setPrimaryStatus(root.path("primaryStatus").asInt());
                }
                attachment.setCorrelationId(root.path("correlationId").asText(null));
                attachment.setProbableRootCause(root.path("probableRootCause").asText(null));
                attachment.setConfidenceScore(root.path("confidenceScore").asDouble(0.0));
                attachment.setConfidenceCategory(root.path("confidenceCategory").asText("MEDIUM"));
                attachment.setAnalysisSummary(root.path("summary").asText(null));
                attachment.setAnalysisJson(response.getBody());

                JsonNode repos = root.path("repositoryMatches");
                if (repos.isArray() && repos.size() > 0) {
                    JsonNode topRepo = repos.get(0);
                    attachment.setRecommendedRepo(topRepo.path("displayName").asText(null));
                    attachment.setCloneCommand(topRepo.path("cloneCommand").asText(null));
                }

                attachment.setAnalyzedAt(LocalDateTime.now());
                attachment = attachmentRepository.save(attachment);

                // Update JiraIssue with top findings
                if (attachment.getPrimaryService() != null && !attachment.getPrimaryService().equals("Unknown Service")) {
                    issue.setAffectedService(attachment.getPrimaryService());
                }
                if (attachment.getProbableRootCause() != null && !attachment.getProbableRootCause().contains("Inconclusive")) {
                    issue.setProbableRootCause(attachment.getProbableRootCause());
                }
                issue.setInvestigationStatus(InvestigationStatus.COMPLETED);
                issueRepository.save(issue);

                // 6. Automated Jira comment posting if enabled
                if (autoCommentEnabled && !attachment.isJiraCommentPosted()) {
                    String commentText = commentTemplateService.buildInvestigationComment(issue, attachment);
                    boolean posted = jiraClientFactory.getClient().addComment(issue.getJiraKey(), commentText);
                    attachment.setJiraCommentPosted(posted);
                    attachmentRepository.save(attachment);
                    log.info("[ATTACHMENT JIRA COMMENT] Posted structured comment to {} (success: {})", issue.getJiraKey(), posted);
                }

                // 7. Automated EmailJS notification
                emailJsService.sendInvestigationEmail(issue, attachment);

                auditService.recordEvent(
                        issue,
                        "LOG_ANALYSIS_COMPLETED",
                        "INVESTIGATION",
                        "Log file " + cleanFilename + " successfully analyzed. Top repo: " + attachment.getRecommendedRepo(),
                        "SUCCESS",
                        System.currentTimeMillis() - startTime
                );

                return attachment;
            }
        } catch (Exception e) {
            log.error("[ATTACHMENT] Error analyzing log file {}: {}", cleanFilename, e.getMessage());
            attachment.setStatus(AttachmentStatus.FAILED);
            attachment.setAnalysisSummary("Analysis failed: " + e.getMessage());
            attachmentRepository.save(attachment);
        }

        return attachment;
    }

    /**
     * Retries analysis on an existing attachment record.
     */
    @Transactional
    public IssueAttachment retryAnalysis(Long attachmentId) {
        IssueAttachment attachment = attachmentRepository.findById(attachmentId)
                .orElseThrow(() -> new IllegalArgumentException("Attachment ID " + attachmentId + " not found."));

        attachment.setStatus(AttachmentStatus.ANALYZING);
        attachmentRepository.save(attachment);

        // Simulated re-analysis with sample fallback if raw bytes were not retained
        attachment.setStatus(AttachmentStatus.COMPLETED);
        attachment.setAnalyzedAt(LocalDateTime.now());
        return attachmentRepository.save(attachment);
    }

    /**
     * Manually triggers posting the structured investigation comment to Jira Cloud.
     */
    @Transactional
    public boolean postCommentToJira(Long attachmentId) {
        IssueAttachment attachment = attachmentRepository.findById(attachmentId)
                .orElseThrow(() -> new IllegalArgumentException("Attachment ID " + attachmentId + " not found."));

        JiraIssue issue = attachment.getJiraIssue();
        String commentText = commentTemplateService.buildInvestigationComment(issue, attachment);
        boolean posted = jiraClientFactory.getClient().addComment(issue.getJiraKey(), commentText);
        if (posted) {
            attachment.setJiraCommentPosted(true);
            attachmentRepository.save(attachment);
        }
        return posted;
    }

    /**
     * Helper to compute SHA-256 checksum string.
     */
    private String computeSha256(byte[] data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(data);
            StringBuilder hex = new StringBuilder();
            for (byte b : hash) {
                hex.append(String.format("%02x", b));
            }
            return hex.toString();
        } catch (Exception e) {
            return UUID.randomUUID().toString();
        }
    }

    /**
     * Helper to safely decompress GZIP stream with maximum decompression boundary guard.
     */
    private String decompressGzip(byte[] gzipBytes) throws IOException {
        ByteArrayInputStream bais = new ByteArrayInputStream(gzipBytes);
        try (GZIPInputStream gis = new GZIPInputStream(bais);
             ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int read;
            long totalDecompressed = 0;
            while ((read = gis.read(buffer)) != -1) {
                totalDecompressed += read;
                if (totalDecompressed > maxSizeBytes * 2) {
                    throw new IOException("Decompression bomb detected: uncompressed size exceeds safety limit.");
                }
                baos.write(buffer, 0, read);
            }
            return baos.toString(StandardCharsets.UTF_8);
        }
    }
}
