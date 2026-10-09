package com.jirapilot.service;

import com.jirapilot.model.dto.PolicyDto;
import com.jirapilot.model.entity.SystemPolicy;
import com.jirapilot.repository.SystemPolicyRepository;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class PolicyService {

    private final SystemPolicyRepository policyRepository;

    @PostConstruct
    public void initDefaultPolicy() {
        if (policyRepository.findByPolicyKey("DEFAULT").isEmpty()) {
            SystemPolicy defaultPolicy = SystemPolicy.builder()
                    .policyKey("DEFAULT")
                    .weightDescription(10)
                    .weightApiDetails(15)
                    .weightLogs(20)
                    .weightRequestPayload(15)
                    .weightEnvironment(10)
                    .weightErrorMessage(10)
                    .weightExpectedActualBehavior(10)
                    .weightReplicationSteps(5)
                    .weightScreenshots(5)
                    .readinessThreshold(70)
                    .confidenceThreshold(75)
                    .similarityThreshold(60)
                    .autoCommentEnabled(true)
                    .autoEmailEnabled(true)
                    .autoInvestigateEnabled(true)
                    .build();
            policyRepository.save(defaultPolicy);
        }
    }

    public PolicyDto getPolicy() {
        SystemPolicy policy = policyRepository.findByPolicyKey("DEFAULT")
                .orElseGet(() -> {
                    initDefaultPolicy();
                    return policyRepository.findByPolicyKey("DEFAULT").get();
                });
        return mapToDto(policy);
    }

    @Transactional
    public PolicyDto updatePolicy(PolicyDto dto) {
        SystemPolicy policy = policyRepository.findByPolicyKey("DEFAULT")
                .orElseGet(() -> SystemPolicy.builder().policyKey("DEFAULT").build());

        policy.setWeightDescription(dto.getWeightDescription());
        policy.setWeightApiDetails(dto.getWeightApiDetails());
        policy.setWeightLogs(dto.getWeightLogs());
        policy.setWeightRequestPayload(dto.getWeightRequestPayload());
        policy.setWeightEnvironment(dto.getWeightEnvironment());
        policy.setWeightErrorMessage(dto.getWeightErrorMessage());
        policy.setWeightExpectedActualBehavior(dto.getWeightExpectedActualBehavior());
        policy.setWeightReplicationSteps(dto.getWeightReplicationSteps());
        policy.setWeightScreenshots(dto.getWeightScreenshots());
        policy.setReadinessThreshold(dto.getReadinessThreshold());
        policy.setConfidenceThreshold(dto.getConfidenceThreshold());
        policy.setSimilarityThreshold(dto.getSimilarityThreshold());
        policy.setAutoCommentEnabled(dto.isAutoCommentEnabled());
        policy.setAutoEmailEnabled(dto.isAutoEmailEnabled());
        policy.setAutoInvestigateEnabled(dto.isAutoInvestigateEnabled());

        policy = policyRepository.save(policy);
        return mapToDto(policy);
    }

    private PolicyDto mapToDto(SystemPolicy entity) {
        return PolicyDto.builder()
                .weightDescription(entity.getWeightDescription())
                .weightApiDetails(entity.getWeightApiDetails())
                .weightLogs(entity.getWeightLogs())
                .weightRequestPayload(entity.getWeightRequestPayload())
                .weightEnvironment(entity.getWeightEnvironment())
                .weightErrorMessage(entity.getWeightErrorMessage())
                .weightExpectedActualBehavior(entity.getWeightExpectedActualBehavior())
                .weightReplicationSteps(entity.getWeightReplicationSteps())
                .weightScreenshots(entity.getWeightScreenshots())
                .readinessThreshold(entity.getReadinessThreshold())
                .confidenceThreshold(entity.getConfidenceThreshold())
                .similarityThreshold(entity.getSimilarityThreshold())
                .autoCommentEnabled(entity.isAutoCommentEnabled())
                .autoEmailEnabled(entity.isAutoEmailEnabled())
                .autoInvestigateEnabled(entity.isAutoInvestigateEnabled())
                .build();
    }
}
