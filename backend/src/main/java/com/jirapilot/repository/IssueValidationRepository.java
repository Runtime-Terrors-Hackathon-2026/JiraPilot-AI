package com.jirapilot.repository;

import com.jirapilot.model.entity.IssueValidation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface IssueValidationRepository extends JpaRepository<IssueValidation, Long> {

    Optional<IssueValidation> findByJiraIssue_JiraKey(String jiraKey);

    @Query("SELECT m, COUNT(m) FROM IssueValidation v JOIN v.missingInformation m GROUP BY m")
    List<Object[]> countMissingInformationFrequency();
}
