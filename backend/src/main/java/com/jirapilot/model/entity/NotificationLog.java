package com.jirapilot.model.entity;

import com.jirapilot.model.enums.NotificationType;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "notification_logs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NotificationLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "jira_issue_id", nullable = false)
    private JiraIssue jiraIssue;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private NotificationType type;

    @Column(length = 128)
    private String recipient;

    @Column(length = 256)
    private String subject;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false, length = 32)
    private String status; // SENT, SIMULATED, FAILED

    @CreationTimestamp
    private LocalDateTime sentAt;
}
