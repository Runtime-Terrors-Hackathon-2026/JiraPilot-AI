package com.jirapilot.controller;

import com.jirapilot.model.dto.PolicyDto;
import com.jirapilot.service.PolicyService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/policies")
@RequiredArgsConstructor
public class PolicyController {

    private final PolicyService policyService;

    @GetMapping
    public ResponseEntity<PolicyDto> getPolicy() {
        return ResponseEntity.ok(policyService.getPolicy());
    }

    @PutMapping
    public ResponseEntity<PolicyDto> updatePolicy(@RequestBody PolicyDto policyDto) {
        return ResponseEntity.ok(policyService.updatePolicy(policyDto));
    }
}
