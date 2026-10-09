package com.jirapilot.repository;

import com.jirapilot.model.entity.IssueAttachment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface IssueAttachmentRepository extends JpaRepository<IssueAttachment, Long> {
    List<IssueAttachment> findByJiraIssue_JiraKeyOrderByCreatedAtDesc(String jiraKey);
    Optional<IssueAttachment> findByJiraIssue_JiraKeyAndSha256Hash(String jiraKey, String sha256Hash);
    Optional<IssueAttachment> findByAttachmentId(String attachmentId);
}
