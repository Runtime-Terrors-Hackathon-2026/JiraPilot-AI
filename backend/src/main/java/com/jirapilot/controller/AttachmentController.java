package com.jirapilot.controller;

import com.jirapilot.model.entity.IssueAttachment;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.repository.IssueAttachmentRepository;
import com.jirapilot.repository.JiraIssueRepository;
import com.jirapilot.service.EmailJsService;
import com.jirapilot.service.JiraCommentTemplateService;
import com.jirapilot.service.LogAttachmentService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class AttachmentController {

    private final LogAttachmentService attachmentService;
    private final IssueAttachmentRepository attachmentRepository;
    private final JiraIssueRepository issueRepository;
    private final JiraCommentTemplateService commentTemplateService;
    private final EmailJsService emailJsService;

    @PostMapping(value = "/issues/{key}/attachments/upload", consumes = org.springframework.http.MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> uploadAttachmentFile(
            @PathVariable String key,
            @RequestParam("file") MultipartFile file
    ) {
        JiraIssue issue = issueRepository.findByJiraKey(key)
                .orElseGet(() -> issueRepository.save(JiraIssue.builder()
                        .jiraKey(key)
                        .summary("Issue " + key)
                        .status(com.jirapilot.model.enums.IssueStatus.OPEN)
                        .build()));

        if (file == null || file.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Uploaded file is empty."));
        }

        try {
            byte[] bytes = file.getBytes();
            String filename = file.getOriginalFilename();
            String mimeType = file.getContentType();

            IssueAttachment attachment = attachmentService.processLogContent(
                    issue,
                    filename,
                    bytes,
                    mimeType,
                    null
            );
            return ResponseEntity.ok(attachment);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            log.error("[ATTACHMENT CONTROLLER] Internal error processing log: ", e);
            return ResponseEntity.internalServerError().body(Map.of("error", "Processing failed: " + e.getMessage()));
        }
    }

    @PostMapping(value = {"/issues/{key}/attachments/upload", "/issues/{key}/attachments/paste"}, consumes = org.springframework.http.MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> uploadAttachmentText(
            @PathVariable String key,
            @RequestBody Map<String, Object> bodyPayload
    ) {
        JiraIssue issue = issueRepository.findByJiraKey(key)
                .orElseGet(() -> issueRepository.save(JiraIssue.builder()
                        .jiraKey(key)
                        .summary("Issue " + key)
                        .status(com.jirapilot.model.enums.IssueStatus.OPEN)
                        .build()));

        if (bodyPayload == null || !bodyPayload.containsKey("logText")) {
            return ResponseEntity.badRequest().body(Map.of("error", "Please provide a 'logText' payload."));
        }

        try {
            Object rawLog = bodyPayload.get("logText");
            String text;
            if (rawLog instanceof Map<?, ?> map && map.containsKey("value")) {
                text = String.valueOf(map.get("value"));
            } else {
                text = String.valueOf(rawLog);
            }
            byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
            String filename = String.valueOf(bodyPayload.getOrDefault("filename", "pasted_telemetry.log"));

            IssueAttachment attachment = attachmentService.processLogContent(
                    issue,
                    filename,
                    bytes,
                    "text/plain",
                    null
            );
            return ResponseEntity.ok(attachment);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            log.error("[ATTACHMENT CONTROLLER] Internal error processing log text: ", e);
            return ResponseEntity.internalServerError().body(Map.of("error", "Processing failed: " + e.getMessage()));
        }
    }

    @GetMapping("/issues/{key}/attachments")
    public ResponseEntity<List<IssueAttachment>> getAttachments(@PathVariable String key) {
        return ResponseEntity.ok(attachmentRepository.findByJiraIssue_JiraKeyOrderByCreatedAtDesc(key));
    }

    @PostMapping("/attachments/{id}/retry")
    public ResponseEntity<IssueAttachment> retryAnalysis(@PathVariable Long id) {
        return ResponseEntity.ok(attachmentService.retryAnalysis(id));
    }

    @GetMapping("/attachments/{id}/comment-preview")
    public ResponseEntity<Map<String, String>> getCommentPreview(@PathVariable Long id) {
        IssueAttachment attachment = attachmentRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Attachment not found"));
        String comment = commentTemplateService.buildInvestigationComment(attachment.getJiraIssue(), attachment);
        return ResponseEntity.ok(Map.of("commentPreview", comment));
    }

    @PostMapping("/attachments/{id}/post-comment")
    public ResponseEntity<Map<String, Object>> postCommentToJira(@PathVariable Long id) {
        boolean success = attachmentService.postCommentToJira(id);
        return ResponseEntity.ok(Map.of(
                "success", success,
                "message", success ? "Comment successfully posted to Jira Cloud" : "Failed to post comment to Jira Cloud"
        ));
    }

    @GetMapping("/attachments/{id}/email-preview")
    public ResponseEntity<Map<String, String>> getEmailPreview(@PathVariable Long id) {
        IssueAttachment attachment = attachmentRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Attachment not found"));
        return ResponseEntity.ok(emailJsService.generateEmailPreview(attachment.getJiraIssue(), attachment));
    }

    @PostMapping("/attachments/{id}/send-email")
    public ResponseEntity<?> sendEmail(@PathVariable Long id) {
        IssueAttachment attachment = attachmentRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Attachment not found"));
        var notificationLog = emailJsService.sendInvestigationEmail(attachment.getJiraIssue(), attachment);
        return ResponseEntity.ok(notificationLog);
    }
}
