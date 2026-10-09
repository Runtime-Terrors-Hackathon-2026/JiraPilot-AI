package com.jirapilot.service;

import com.jirapilot.model.entity.AuditEvent;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.repository.AuditEventRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditService {

    private final AuditEventRepository auditEventRepository;

    @Transactional
    public void recordEvent(JiraIssue issue, String eventType, String stage, String details, String status, Long durationMs) {
        String jiraKey = issue != null ? issue.getJiraKey() : "SYSTEM";
        log.info("[AUDIT] jiraKey={} eventType={} stage={} status={} duration={}ms - {}",
                jiraKey, eventType, stage, status, durationMs, details);

        AuditEvent event = AuditEvent.builder()
                .jiraIssue(issue)
                .jiraKey(jiraKey)
                .eventType(eventType)
                .workflowStage(stage)
                .details(details)
                .status(status)
                .durationMs(durationMs)
                .build();

        auditEventRepository.save(event);
    }

    public List<AuditEvent> getEventsForIssue(String jiraKey) {
        return auditEventRepository.findByJiraKeyOrderByTimestampAsc(jiraKey);
    }
}
