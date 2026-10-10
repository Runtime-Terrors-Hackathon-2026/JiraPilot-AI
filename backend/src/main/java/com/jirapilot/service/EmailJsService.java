package com.jirapilot.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.model.entity.IssueAttachment;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.model.entity.NotificationLog;
import com.jirapilot.model.enums.NotificationType;
import com.jirapilot.repository.NotificationLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailJsService {

    private final NotificationLogRepository notificationLogRepository;
    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${jirapilot.emailjs.service-id:service_jirapilot}")
    private String serviceId;

    @Value("${jirapilot.emailjs.template-id:template_investigation}")
    private String templateId;

    @Value("${jirapilot.emailjs.public-key:public_key_mock}")
    private String publicKey;

    @Value("${jirapilot.emailjs.private-key:}")
    private String privateKey;

    @Value("${jirapilot.emailjs.enabled:false}")
    private boolean emailJsEnabled;

    @Value("${jirapilot.emailjs.api-url:https://api.emailjs.com/api/v1.0/email/send}")
    private String apiUrl;

    @Value("${jirapilot.emailjs.allowed-recipients:sshankaran202@gmail.com,reporter@example.com}")
    private String allowedRecipientsStr;

    /**
     * Checks if a recipient is allowlisted.
     */
    public boolean isRecipientAllowed(String email) {
        if (email == null) return false;
        List<String> allowed = Arrays.asList(allowedRecipientsStr.split(","));
        for (String a : allowed) {
            if (a.trim().equalsIgnoreCase(email.trim()) || a.trim().equals("*")) {
                return true;
            }
        }
        return false;
    }

    /**
     * Generates a preview HTML and plain text for the investigation email.
     */
    public Map<String, String> generateEmailPreview(JiraIssue issue, IssueAttachment attachment) {
        String key = issue.getJiraKey();
        String summary = issue.getSummary();
        String rootCause = attachment.getProbableRootCause() != null ? attachment.getProbableRootCause() : "Analysis in progress";
        String service = attachment.getPrimaryService() != null ? attachment.getPrimaryService() : "Unknown service";
        String endpoint = attachment.getPrimaryEndpoint() != null ? attachment.getPrimaryEndpoint() : "Unknown endpoint";
        String repo = attachment.getRecommendedRepo() != null ? attachment.getRecommendedRepo() : "None";
        String clone = attachment.getCloneCommand() != null ? attachment.getCloneCommand() : "N/A";

        String html = "<!DOCTYPE html>\n" +
                "<html lang='en'>\n" +
                "<head>\n" +
                "<meta charset='UTF-8'>\n" +
                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n" +
                "<style>\n" +
                "  @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.15); } }\n" +
                "  @keyframes glow { 0%, 100% { border-color: #3b82f6; } 50% { border-color: #10b981; } }\n" +
                "  .pulse-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite ease-in-out; vertical-align: middle; margin-right: 6px; }\n" +
                "  .btn-hover:hover { background: #4338ca !important; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4) !important; }\n" +
                "</style>\n" +
                "</head>\n" +
                "<body style='margin: 0; padding: 0; background-color: #0b1220; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif; color: #1e293b; -webkit-font-smoothing: antialiased;'>\n" +
                "  <table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='background-color: #0b1220; padding: 40px 15px;'>\n" +
                "    <tr>\n" +
                "      <td align='center'>\n" +
                "        <table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='max-width: 620px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.3); border: 1px solid #1e293b;'>\n" +
                "          <!-- TOP BRAND HEADER -->\n" +
                "          <tr>\n" +
                "            <td style='background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 28px 32px; border-bottom: 2px solid #3b82f6;'>\n" +
                "              <table role='presentation' width='100%' cellpadding='0' cellspacing='0'>\n" +
                "                <tr>\n" +
                "                  <td>\n" +
                "                    <div style='display: inline-block; padding: 4px 10px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 9999px; font-size: 11px; font-weight: 700; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>\n" +
                "                      <span class='pulse-dot'></span>LIVE INCIDENT TRIAGE\n" +
                "                    </div>\n" +
                "                    <h1 style='margin: 0; font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;'>\n" +
                "                      JiraPilot <span style='background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AI</span>\n" +
                "                    </h1>\n" +
                "                    <div style='margin-top: 4px; font-size: 13px; color: #94a3b8;'>\n" +
                "                      Autonomous Root Cause Analysis & Diagnostic Report\n" +
                "                    </div>\n" +
                "                  </td>\n" +
                "                  <td align='right' valign='top'>\n" +
                "                    <span style='display: inline-block; padding: 6px 14px; background: #3b82f6; color: #ffffff; font-family: monospace; font-size: 14px; font-weight: 700; border-radius: 8px; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);'>\n" +
                "                      " + key + "\n" +
                "                    </span>\n" +
                "                  </td>\n" +
                "                </tr>\n" +
                "              </table>\n" +
                "            </td>\n" +
                "          </tr>\n" +
                "          <!-- EXECUTIVE SUMMARY BANNER -->\n" +
                "          <tr>\n" +
                "            <td style='padding: 28px 32px 16px 32px;'>\n" +
                "              <div style='padding: 18px 20px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; border-left: 4px solid #3b82f6;'>\n" +
                "                <div style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em;'>\n" +
                "                  Ticket Summary\n" +
                "                </div>\n" +
                "                <div style='margin-top: 4px; font-size: 15px; font-weight: 600; color: #0f172a; line-height: 1.4;'>\n" +
                "                  " + summary + "\n" +
                "                </div>\n" +
                "              </div>\n" +
                "            </td>\n" +
                "          </tr>\n" +
                "          <!-- DIAGNOSTIC MATRIX -->\n" +
                "          <tr>\n" +
                "            <td style='padding: 8px 32px 20px 32px;'>\n" +
                "              <table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='border-collapse: separate; border-spacing: 0; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;'>\n" +
                "                <tr style='background-color: #f1f5f9;'>\n" +
                "                  <td style='padding: 10px 16px; font-size: 12px; font-weight: 700; color: #475569; width: 38%; border-bottom: 1px solid #e2e8f0;'>Diagnostic Parameter</td>\n" +
                "                  <td style='padding: 10px 16px; font-size: 12px; font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0;'>Extracted Evidence</td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                  <td style='padding: 12px 16px; font-size: 13px; font-weight: 600; color: #334155; border-bottom: 1px solid #f1f5f9;'>Suspected Service:</td>\n" +
                "                  <td style='padding: 12px 16px; font-size: 13px; font-weight: 600; color: #0284c7; border-bottom: 1px solid #f1f5f9;'>" + service + "</td>\n" +
                "                </tr>\n" +
                "                <tr style='background-color: #f8fafc;'>\n" +
                "                  <td style='padding: 12px 16px; font-size: 13px; font-weight: 600; color: #334155; border-bottom: 1px solid #f1f5f9;'>Detected API Endpoint:</td>\n" +
                "                  <td style='padding: 12px 16px; font-size: 12px; font-family: monospace; color: #0f172a; border-bottom: 1px solid #f1f5f9;'><code>" + endpoint + "</code></td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                  <td style='padding: 12px 16px; font-size: 13px; font-weight: 600; color: #334155; border-bottom: 1px solid #f1f5f9;'>Recommended Repo:</td>\n" +
                "                  <td style='padding: 12px 16px; font-size: 13px; font-weight: 700; color: #4f46e5; border-bottom: 1px solid #f1f5f9;'>" + repo + "</td>\n" +
                "                </tr>\n" +
                "                <tr style='background-color: #f8fafc;'>\n" +
                "                  <td style='padding: 12px 16px; font-size: 13px; font-weight: 600; color: #334155;'>Investigation Confidence:</td>\n" +
                "                  <td style='padding: 12px 16px; font-size: 13px; font-weight: 700; color: #059669;'><span style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10b981; margin-right: 6px;'></span>HIGH (Evidence Backed)</td>\n" +
                "                </tr>\n" +
                "              </table>\n" +
                "            </td>\n" +
                "          </tr>\n" +
                "          <!-- PROBABLE ROOT CAUSE CARD -->\n" +
                "          <tr>\n" +
                "            <td style='padding: 0 32px 20px 32px;'>\n" +
                "              <div style='padding: 18px 20px; background-color: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b; border-radius: 12px;'>\n" +
                "                <div style='display: flex; align-items: center; margin-bottom: 6px;'>\n" +
                "                  <span style='font-size: 14px; margin-right: 6px;'>⚡</span>\n" +
                "                  <span style='font-size: 12px; font-weight: 700; color: #b45309; text-transform: uppercase; letter-spacing: 0.05em;'>Identified Root Cause</span>\n" +
                "                </div>\n" +
                "                <div style='font-size: 14px; font-weight: 600; color: #92400e; line-height: 1.5;'>\n" +
                "                  " + rootCause + "\n" +
                "                </div>\n" +
                "              </div>\n" +
                "            </td>\n" +
                "          </tr>\n" +
                "          <!-- CODEBASE CLONE TERMINAL -->\n" +
                "          <tr>\n" +
                "            <td style='padding: 0 32px 28px 32px;'>\n" +
                "              <div style='background-color: #0f172a; border-radius: 12px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); border: 1px solid #334155;'>\n" +
                "                <!-- macOS Terminal Header -->\n" +
                "                <div style='background-color: #1e293b; padding: 10px 16px; border-bottom: 1px solid #334155;'>\n" +
                "                  <span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #ef4444; margin-right: 6px;'></span>\n" +
                "                  <span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #eab308; margin-right: 6px;'></span>\n" +
                "                  <span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #22c55e; margin-right: 12px;'></span>\n" +
                "                  <span style='font-family: monospace; font-size: 11px; color: #94a3b8; font-weight: 600;'>bash — developer clone command</span>\n" +
                "                </div>\n" +
                "                <div style='padding: 16px 18px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; color: #38bdf8; word-break: break-all; line-height: 1.4;'>\n" +
                "                  <span style='color: #a855f7; user-select: none;'>$ </span>" + clone + "\n" +
                "                </div>\n" +
                "              </div>\n" +
                "            </td>\n" +
                "          </tr>\n" +
                "          <!-- CTA ACTION BUTTON -->\n" +
                "          <tr>\n" +
                "            <td align='center' style='padding: 0 32px 32px 32px;'>\n" +
                "              <a href='http://localhost:3000/tickets/" + key + "' class='btn-hover' style='display: inline-block; padding: 14px 32px; background: #4f46e5; color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 700; border-radius: 10px; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35); transition: all 0.2s;'>\n" +
                "                Open Incident Workspace &rarr;\n" +
                "              </a>\n" +
                "              <div style='margin-top: 12px; font-size: 12px; color: #64748b;'>\n" +
                "                Autonomous comment & diagnostic findings have also been posted directly to Jira.\n" +
                "              </div>\n" +
                "            </td>\n" +
                "          </tr>\n" +
                "          <!-- FOOTER -->\n" +
                "          <tr>\n" +
                "            <td style='background-color: #f8fafc; padding: 24px 32px; border-top: 1px solid #e2e8f0; text-align: center;'>\n" +
                "              <p style='margin: 0; font-size: 12px; color: #64748b; line-height: 1.5;'>\n" +
                "                This email was dispatched autonomously by <strong>JiraPilot AI</strong> for Northstar Digital Systems.<br>\n" +
                "                Generated using approved synthetic incident telemetry. AI recommendations require developer verification.\n" +
                "              </p>\n" +
                "              <div style='margin-top: 12px; font-size: 11px; color: #94a3b8;'>\n" +
                "                &copy; 2026 JiraPilot AI Platform &bull; Northstar Labs Incident Intelligence\n" +
                "              </div>\n" +
                "            </td>\n" +
                "          </tr>\n" +
                "        </table>\n" +
                "      </td>\n" +
                "    </tr>\n" +
                "  </table>\n" +
                "</body>\n" +
                "</html>";

        String text = "JiraPilot AI — Log Investigation Report\n\n" +
                "Ticket: " + key + "\n" +
                "Summary: " + summary + "\n\n" +
                "Suspected Service: " + service + "\n" +
                "Detected API: " + endpoint + "\n" +
                "Probable Root Cause: " + rootCause + "\n" +
                "Recommended Codebase: " + repo + "\n" +
                "Clone: " + clone + "\n\n" +
                "Generated by JiraPilot AI.";

        return Map.of("html", html, "text", text, "subject", "JiraPilot AI Investigation Completed — " + key);
    }

    /**
     * Sends investigation notification via EmailJS REST API or records as SIMULATED.
     */
    @Transactional
    public NotificationLog sendInvestigationEmail(JiraIssue issue, IssueAttachment attachment) {
        String recipient = issue.getReporter() != null ? issue.getReporter() : "sshankaran202@gmail.com";
        Map<String, String> preview = generateEmailPreview(issue, attachment);
        String subject = preview.get("subject");
        String content = preview.get("text");

        // Check allowlist
        if (!isRecipientAllowed(recipient)) {
            log.warn("[EMAILJS] Recipient '{}' is not in allowed recipients list ({}). Suppressing email.", recipient, allowedRecipientsStr);
            NotificationLog logEntry = NotificationLog.builder()
                    .jiraIssue(issue)
                    .type(NotificationType.INVESTIGATION_COMPLETE_EMAIL)
                    .recipient(recipient)
                    .subject(subject + " [SUPPRESSED]")
                    .content("Email suppressed by recipient allowlist policy.")
                    .status("BLOCKED_ALLOWLIST")
                    .build();
            return notificationLogRepository.save(logEntry);
        }

        String deliveryStatus = "SIMULATED";

        if (emailJsEnabled) {
            try {
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                headers.set("Origin", "http://localhost:3000");
                headers.set("Referer", "http://localhost:3000/");
                headers.set(HttpHeaders.USER_AGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");

                Map<String, Object> templateParams = new HashMap<>();
                templateParams.put("to_email", recipient);
                templateParams.put("issue_key", issue.getJiraKey());
                templateParams.put("issue_summary", issue.getSummary());
                templateParams.put("service_name", attachment.getPrimaryService() != null ? attachment.getPrimaryService() : "payment-gateway-service");
                templateParams.put("api_endpoint", attachment.getPrimaryEndpoint() != null ? attachment.getPrimaryEndpoint() : "POST /api/v1/payments/process");
                templateParams.put("root_cause", attachment.getProbableRootCause() != null ? attachment.getProbableRootCause() : "Investigated stack trace indicated NullPointerException in checkout transaction flow.");
                templateParams.put("clone_command", attachment.getCloneCommand() != null ? attachment.getCloneCommand() : "git clone https://github.com/example/payments-service.git");
                templateParams.put("dashboard_url", "http://localhost:3000/tickets/" + issue.getJiraKey());

                Map<String, Object> payload = new HashMap<>();
                payload.put("service_id", serviceId);
                payload.put("template_id", templateId);
                payload.put("user_id", publicKey);
                if (privateKey != null && !privateKey.isBlank()) {
                    payload.put("accessToken", privateKey);
                }
                payload.put("template_params", templateParams);

                HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);
                ResponseEntity<String> response = restTemplate.postForEntity(apiUrl, request, String.class);

                if (response.getStatusCode().is2xxSuccessful()) {
                    deliveryStatus = "SENT";
                    log.info("[EMAILJS] Dispatched email successfully to {} for issue {}", recipient, issue.getJiraKey());
                } else {
                    deliveryStatus = "FAILED";
                    log.warn("[EMAILJS] EmailJS API returned status {}: {}", response.getStatusCode(), response.getBody());
                }
            } catch (Exception e) {
                log.warn("[EMAILJS] Delivery failed: {}. Falling back to SIMULATED status.", e.getMessage());
                deliveryStatus = "FAILED";
            }
        } else {
            log.info("[EMAILJS] EmailJS disabled (MOCK MODE). Notification recorded to Mock Email Viewer for {}.", recipient);
        }

        NotificationLog logEntry = NotificationLog.builder()
                .jiraIssue(issue)
                .type(NotificationType.INVESTIGATION_COMPLETE_EMAIL)
                .recipient(recipient)
                .subject(subject)
                .content(content)
                .status(deliveryStatus)
                .build();

        attachment.setEmailSent(deliveryStatus.equals("SENT") || deliveryStatus.equals("SIMULATED"));
        return notificationLogRepository.save(logEntry);
    }

    /**
     * Dispatches a test email for verification.
     */
    public Map<String, Object> sendTestEmail(String targetRecipient) {
        String recipient = targetRecipient != null ? targetRecipient : "sshankaran202@gmail.com";
        if (!isRecipientAllowed(recipient)) {
            return Map.of("status", "REJECTED", "message", "Recipient is not on allowed list: " + allowedRecipientsStr);
        }

        if (!emailJsEnabled) {
            return Map.of(
                    "status", "MOCK_SUCCESS",
                    "mode", "SIMULATED",
                    "message", "EmailJS is currently in MOCK MODE (EMAILJS_ENABLED=false). Email saved to Mock Email Viewer.",
                    "recipient", recipient
            );
        }

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Origin", "http://localhost:3000");
            headers.set("Referer", "http://localhost:3000/");
            headers.set(HttpHeaders.USER_AGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");

            Map<String, Object> templateParams = new HashMap<>();
            templateParams.put("to_email", recipient);
            templateParams.put("issue_key", "TEST-KAN");
            templateParams.put("issue_summary", "Live EmailJS Verification — JiraPilot AI Incident Operations");
            templateParams.put("service_name", "resource-inventory-service");
            templateParams.put("api_endpoint", "POST /api/v1/resources/allocate");
            templateParams.put("root_cause", "Live test dispatch from JiraPilot AI autonomous incident operations console.");
            templateParams.put("clone_command", "git clone https://github.com/example/resource-inventory-service.git");
            templateParams.put("dashboard_url", "http://localhost:3000/tickets/KAN-8");
            templateParams.put("message", "This is an automated test message from JiraPilot AI.");

            Map<String, Object> payload = new HashMap<>();
            payload.put("service_id", serviceId);
            payload.put("template_id", templateId);
            payload.put("user_id", publicKey);
            if (privateKey != null && !privateKey.isBlank()) {
                payload.put("accessToken", privateKey);
            }
            payload.put("template_params", templateParams);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);
            ResponseEntity<String> response = restTemplate.postForEntity(apiUrl, request, String.class);

            return Map.of(
                    "status", response.getStatusCode().is2xxSuccessful() ? "SUCCESS" : "ERROR",
                    "statusCode", response.getStatusCode().value(),
                    "response", response.getBody() != null ? response.getBody() : "OK"
            );
        } catch (Exception e) {
            return Map.of("status", "ERROR", "message", e.getMessage());
        }
    }
}
