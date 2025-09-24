FROM openjdk:17-jdk-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy Maven wrapper and pom.xml first for better caching
COPY .mvn/ .mvn/
COPY mvnw pom.xml ./
RUN chmod +x mvnw

# Download dependencies
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src ./src

# Build application
RUN ./mvnw clean package -DskipTests

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy built jar
RUN cp target/*.jar app.jar && chown appuser:appuser app.jar

USER appuser

EXPOSE 8087

ENTRYPOINT ["java", "-jar", "app.jar"]