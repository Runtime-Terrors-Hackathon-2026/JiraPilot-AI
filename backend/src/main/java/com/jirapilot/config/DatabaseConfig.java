package com.jirapilot.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.env.Environment;

import javax.sql.DataSource;
import java.net.URI;

@Slf4j
@Configuration
public class DatabaseConfig {

    @Bean
    @Primary
    public DataSource dataSource(DataSourceProperties properties, Environment env) {
        String rawUrl = env.getProperty("DATABASE_URL");
        if (rawUrl != null && !rawUrl.isBlank()) {
            if (rawUrl.startsWith("postgres://") || rawUrl.startsWith("postgresql://")) {
                try {
                    log.info("[DATABASE CONFIG] Detected cloud PostgreSQL connection string. Normalizing for JDBC...");
                    String normalized = rawUrl.replace("postgres://", "http://").replace("postgresql://", "http://");
                    URI uri = new URI(normalized);
                    String host = uri.getHost();
                    int port = uri.getPort() > 0 ? uri.getPort() : 5432;
                    String path = uri.getPath();
                    String userInfo = uri.getUserInfo();

                    String username = properties.getUsername();
                    String password = properties.getPassword();
                    if (userInfo != null && userInfo.contains(":")) {
                        String[] parts = userInfo.split(":", 2);
                        username = parts[0];
                        password = parts[1];
                    }

                    String jdbcUrl = "jdbc:postgresql://" + host + ":" + port + path;
                    properties.setUrl(jdbcUrl);
                    properties.setDriverClassName("org.postgresql.Driver");
                    if (username != null) properties.setUsername(username);
                    if (password != null) properties.setPassword(password);
                    log.info("[DATABASE CONFIG] Configured PostgreSQL JDBC URL: {}", jdbcUrl);
                } catch (Exception e) {
                    log.warn("[DATABASE CONFIG] Failed to parse DATABASE_URL as URI: {}. Proceeding with default properties.", e.getMessage());
                }
            }
        }
        return properties.initializeDataSourceBuilder().build();
    }
}
