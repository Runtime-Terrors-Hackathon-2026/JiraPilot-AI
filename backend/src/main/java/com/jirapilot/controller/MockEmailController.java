package com.jirapilot.controller;

import com.jirapilot.model.dto.MockEmailDto;
import com.jirapilot.service.EmailNotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/notifications")
@RequiredArgsConstructor
public class MockEmailController {

    private final EmailNotificationService emailService;

    @GetMapping("/emails")
    public ResponseEntity<List<MockEmailDto>> getAllEmails() {
        return ResponseEntity.ok(emailService.getAllMockEmails());
    }

    @GetMapping("/emails/{key}")
    public ResponseEntity<List<MockEmailDto>> getEmailsForIssue(@PathVariable String key) {
        return ResponseEntity.ok(emailService.getEmailsForIssue(key));
    }
}
