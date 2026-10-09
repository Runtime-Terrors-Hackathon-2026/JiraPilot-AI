package com.jirapilot.repository;

import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.model.enums.InvestigationStatus;
import com.jirapilot.model.enums.IssueStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface JiraIssueRepository extends JpaRepository<JiraIssue, Long> {

    Optional<JiraIssue> findByJiraKey(String jiraKey);

    List<JiraIssue> findAllByOrderByCreatedAtDesc();

    long countByStatus(IssueStatus status);

    long countByInvestigationStatus(InvestigationStatus status);

    @Query("SELECT AVG(i.readinessScore) FROM JiraIssue i WHERE i.readinessScore IS NOT NULL")
    Double calculateAverageReadinessScore();

    @Query("SELECT i.affectedService, COUNT(i) FROM JiraIssue i WHERE i.affectedService IS NOT NULL GROUP BY i.affectedService")
    List<Object[]> countByAffectedService();

    @Query("SELECT i.probableRootCause, COUNT(i) FROM JiraIssue i WHERE i.probableRootCause IS NOT NULL GROUP BY i.probableRootCause")
    List<Object[]> countByRootCause();
}
