# ==============================================================================
# JiraPilot AI - Root Dockerfile for Render Web Service (Java 21 Spring Boot)
# ==============================================================================

FROM maven:3.9.6-eclipse-temurin-21-alpine AS build
WORKDIR /app

# Copy settings.xml with Google Cloud Mirror to prevent HTTP 429 Rate Limiting
COPY settings.xml .
COPY backend/pom.xml .
COPY backend/src ./src
COPY demo-data ./demo-data

# Build production executable JAR using Google Cloud Mirror
RUN mvn clean package -DskipTests --settings settings.xml -B

# Minimal production JRE runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Install curl for health checking
RUN apk add --no-cache curl tzdata

# Copy built artifact and demo data
COPY --from=build /app/target/*.jar app.jar
COPY --from=build /app/demo-data ./demo-data

# Environment configuration
ENV PORT=8080
ENV SPRING_PROFILES_ACTIVE=dev
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75.0 -XX:+UseG1GC -Djava.security.egd=file:/dev/./urandom"

EXPOSE 8080

# Dynamic port binding for Render ($PORT)
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Dserver.port=${PORT:-8080} -jar app.jar"]
