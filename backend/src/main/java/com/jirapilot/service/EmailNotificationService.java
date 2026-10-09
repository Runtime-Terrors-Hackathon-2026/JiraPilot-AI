package com.jirapilot.service;

import com.jirapilot.model.dto.MockEmailDto;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.model.entity.NotificationLog;
import com.jirapilot.model.enums.NotificationType;
import com.jirapilot.repository.NotificationLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailNotificationService {

    private final NotificationLogRepository notificationLogRepository;
    private final JavaMailSender mailSender;

    @Value("${jirapilot.email-notifications-enabled:true}")
    private boolean emailEnabled;

    @Value("${jirapilot.demo-mode:true}")
    private boolean demoMode;

    @Value("${spring.mail.username:notifications@jirapilot.ai}")
    private String fromEmail;

    @Transactional
    public NotificationLog sendMissingInformationEmail(JiraIssue issue, String emailBody) {
        String recipient = issue.getReporter() != null ? issue.getReporter() : "reporter@example.com";
        String subject = "Additional Information Required — " + issue.getJiraKey();

        String status = "SIMULATED";
        if (emailEnabled && !demoMode) {
            try {
                SimpleMailMessage message = new SimpleMailMessage();
                message.setFrom(fromEmail);
                message.setTo(recipient);
                message.setSubject(subject);
                message.setText(emailBody);
                mailSender.send(message);
                status = "SENT";
                log.info("[EMAIL] Successfully dispatched missing info notification to {}", recipient);
            } catch (Exception e) {
                log.warn("[EMAIL] Failed to send email via SMTP (recorded in Mock Email Viewer): {}", e.getMessage());
                status = "SIMULATED";
            }
        } else {
            log.info("[EMAIL MOCK] Email saved to Mock Viewer for {}: {}", recipient, subject);
        }

        NotificationLog logEntry = NotificationLog.builder()
                .jiraIssue(issue)
                .type(NotificationType.MISSING_INFO_EMAIL)
                .recipient(recipient)
                .subject(subject)
                .content(emailBody)
                .status(status)
                .build();

        return notificationLogRepository.save(logEntry);
    }

    @Transactional
    public NotificationLog sendInvestigationCompletedEmail(JiraIssue issue, String summary) {
        String recipient = issue.getReporter() != null ? issue.getReporter() : "reporter@example.com";
        String subject = "Investigation Completed — " + issue.getJiraKey();

        NotificationLog logEntry = NotificationLog.builder()
                .jiraIssue(issue)
                .type(NotificationType.INVESTIGATION_COMPLETE_EMAIL)
                .recipient(recipient)
                .subject(subject)
                .content(summary)
                .status("SIMULATED")
                .build();

        return notificationLogRepository.save(logEntry);
    }

    public List<MockEmailDto> getAllMockEmails() {
        return notificationLogRepository.findAllByOrderBySentAtDesc().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    public List<MockEmailDto> getEmailsForIssue(String jiraKey) {
        return notificationLogRepository.findByJiraIssue_JiraKeyOrderBySentAtDesc(jiraKey).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    private MockEmailDto mapToDto(NotificationLog log) {
        return MockEmailDto.builder()
                .id(log.getId())
                .jiraKey(log.getJiraIssue() != null ? log.getJiraIssue().getJiraKey() : "SYSTEM")
                .recipient(log.getRecipient())
                .subject(log.getSubject())
                .content(log.getContent())
                .status(log.getStatus())
                .sentAt(log.getSentAt())
                .build();
    }
}
