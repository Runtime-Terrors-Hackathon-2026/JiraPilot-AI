package com.jirapilot.controller;

import com.jirapilot.service.KnowledgeService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {

    private final KnowledgeService knowledgeService;

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getKnowledgeBase() {
        return ResponseEntity.ok(knowledgeService.getAllKnowledge());
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> addKnowledgeRecord(@RequestBody Map<String, Object> record) {
        knowledgeService.saveKnowledge(record);
        return ResponseEntity.ok(Map.of("status", "SUCCESS", "message", "Knowledge record saved"));
    }
}
