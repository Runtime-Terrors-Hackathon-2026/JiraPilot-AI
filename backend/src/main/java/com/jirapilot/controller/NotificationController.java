package com.jirapilot.controller;

import com.jirapilot.service.EmailJsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final EmailJsService emailJsService;

    @PostMapping("/test-email")
    public ResponseEntity<Map<String, Object>> sendTestEmail(@RequestBody(required = false) Map<String, String> request) {
        String recipient = request != null ? request.get("recipient") : null;
        return ResponseEntity.ok(emailJsService.sendTestEmail(recipient));
    }
}
