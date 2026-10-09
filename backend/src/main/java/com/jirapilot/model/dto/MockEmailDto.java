package com.jirapilot.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MockEmailDto {
    private Long id;
    private String jiraKey;
    private String recipient;
    private String subject;
    private String content;
    private String status;
    private LocalDateTime sentAt;
}
