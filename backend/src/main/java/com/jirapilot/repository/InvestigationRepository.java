package com.jirapilot.repository;

import com.jirapilot.model.entity.Investigation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface InvestigationRepository extends JpaRepository<Investigation, Long> {
    Optional<Investigation> findByJiraIssue_JiraKey(String jiraKey);
}
