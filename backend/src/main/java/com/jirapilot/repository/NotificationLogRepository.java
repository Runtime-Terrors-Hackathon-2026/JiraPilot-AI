package com.jirapilot.repository;

import com.jirapilot.model.entity.NotificationLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface NotificationLogRepository extends JpaRepository<NotificationLog, Long> {
    List<NotificationLog> findByJiraIssue_JiraKeyOrderBySentAtDesc(String jiraKey);
    List<NotificationLog> findAllByOrderBySentAtDesc();
}
