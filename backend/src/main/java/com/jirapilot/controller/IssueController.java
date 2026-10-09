package com.jirapilot.controller;

import com.jirapilot.model.dto.*;
import com.jirapilot.service.IssueService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/issues")
@RequiredArgsConstructor
public class IssueController {

    private final IssueService issueService;

    @GetMapping
    public ResponseEntity<List<IssueResponseDto>> getAllIssues() {
        return ResponseEntity.ok(issueService.getAllIssues());
    }

    @GetMapping("/{key}")
    public ResponseEntity<IssueResponseDto> getIssue(@PathVariable String key) {
        return issueService.getIssueByKey(key)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<IssueResponseDto> createOrUpdateIssue(@RequestBody CreateIssueRequest request) {
        return ResponseEntity.ok(issueService.createOrUpdateIssue(request));
    }

    @PostMapping("/{key}/validate")
    public ResponseEntity<ValidationResultDto> revalidateIssue(@PathVariable String key) {
        return ResponseEntity.ok(issueService.revalidateIssue(key));
    }

    @PostMapping("/{key}/investigate")
    public ResponseEntity<InvestigationResultDto> investigateIssue(@PathVariable String key) {
        return ResponseEntity.ok(issueService.investigateIssue(key));
    }

    @PostMapping("/{key}/comment")
    public ResponseEntity<Boolean> postComment(@PathVariable String key, @RequestBody PostCommentRequest request) {
        return ResponseEntity.ok(issueService.addComment(key, request.getComment()));
    }

    @PostMapping("/jira/sync")
    public ResponseEntity<List<IssueResponseDto>> syncJiraProject(@RequestParam(defaultValue = "KAN") String projectKey) {
        return ResponseEntity.ok(issueService.syncJiraProject(projectKey));
    }
}
