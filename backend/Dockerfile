# ==============================================================================
# JiraPilot AI - Java 21 Spring Boot Backend Dockerfile for Render / Cloud
# ==============================================================================

# Stage 1: Build the Spring Boot JAR with Google Cloud Maven Mirror
FROM maven:3.9.6-eclipse-temurin-21-alpine AS build
WORKDIR /app

# Copy settings.xml with Google Cloud Mirror to prevent HTTP 429 Rate Limiting
COPY settings.xml .
COPY pom.xml .
COPY src ./src
COPY demo-data ./demo-data

# Build production executable JAR using Google Cloud Mirror (no rate limits)
RUN mvn clean package -DskipTests --settings settings.xml -B

# Stage 2: Ultra-lightweight Production JRE Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Install curl for container health checks
RUN apk add --no-cache curl tzdata

# Copy built artifact and demo data from build stage
COPY --from=build /app/target/*.jar app.jar
COPY --from=build /app/demo-data ./demo-data

# Default cloud environment configuration
ENV PORT=8080
ENV SPRING_PROFILES_ACTIVE=dev
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75.0 -XX:+UseG1GC -Djava.security.egd=file:/dev/./urandom"

# Expose dynamic application port
EXPOSE 8080

# Dynamic port binding for Render ($PORT)
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Dserver.port=${PORT:-8080} -jar app.jar"]
