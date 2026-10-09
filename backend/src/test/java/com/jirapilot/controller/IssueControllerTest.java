package com.jirapilot.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.model.dto.CreateIssueRequest;
import com.jirapilot.model.dto.IssueResponseDto;
import com.jirapilot.model.enums.IssueStatus;
import com.jirapilot.service.IssueService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(IssueController.class)
public class IssueControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private IssueService issueService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void shouldReturnAllIssues() throws Exception {
        IssueResponseDto issue = IssueResponseDto.builder()
                .jiraKey("HACK-1001")
                .summary("Circuit API failure")
                .status(IssueStatus.READY)
                .build();

        when(issueService.getAllIssues()).thenReturn(List.of(issue));

        mockMvc.perform(get("/api/issues"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].jiraKey").value("HACK-1001"));
    }

    @Test
    void shouldCreateOrUpdateIssue() throws Exception {
        CreateIssueRequest req = CreateIssueRequest.builder()
                .key("HACK-1001")
                .summary("Circuit API failure")
                .build();

        IssueResponseDto res = IssueResponseDto.builder()
                .jiraKey("HACK-1001")
                .summary("Circuit API failure")
                .status(IssueStatus.READY)
                .build();

        when(issueService.createOrUpdateIssue(any())).thenReturn(res);

        mockMvc.perform(post("/api/issues")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.jiraKey").value("HACK-1001"));
    }
}
