package com.jirapilot.repository;

import com.jirapilot.model.entity.AuditEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AuditEventRepository extends JpaRepository<AuditEvent, Long> {
    List<AuditEvent> findByJiraKeyOrderByTimestampAsc(String jiraKey);
    List<AuditEvent> findAllByOrderByTimestampDesc();
}
