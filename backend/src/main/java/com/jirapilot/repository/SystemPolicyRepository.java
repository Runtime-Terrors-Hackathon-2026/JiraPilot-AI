package com.jirapilot.repository;

import com.jirapilot.model.entity.SystemPolicy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface SystemPolicyRepository extends JpaRepository<SystemPolicy, Long> {
    Optional<SystemPolicy> findByPolicyKey(String policyKey);
}
