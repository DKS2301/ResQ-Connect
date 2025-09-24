# ResQConnect Transformation Plan

## Overview
Transform the retail store microservices architecture into ResQConnect (Community Calamity Response Network) while maintaining the exact same CI/CD and deployment strategy.

## Service Transformation Mapping

### Phase 1: Core Service Transformation (Existing Services)

| Current Service | ResQConnect Service | Language | Port | Purpose |
|----------------|-------------------|----------|------|---------|
| **UI** → **Coordinator UI** | Java (Spring Boot) | 8080 | Web interface for coordinators |
| **Catalog** → **Request Service** | Go | 8081 | CRUD for disaster requests |
| **Cart** → **Volunteer Service** | Java (Spring Boot) | 8082 | Volunteer profiles & availability |
| **Orders** → **Matching Service** | Java (Spring Boot) | 8083 | Match requests to volunteers |
| **Checkout** → **Notification Service** | Node.js (NestJS) | 8084 | Push/SMS notifications |

### Phase 2: New Services (Additional)

| Service | Language | Port | Purpose |
|---------|----------|------|---------|
| **Ingest Service** | Python (FastAPI) | 8085 | SMS/WhatsApp/Forms ingestion |
| **NLP Service** | Python (FastAPI) | 8086 | Intent extraction & geocoding |
| **Graph Service** | Java (Spring Boot) | 8087 | Neo4j access layer |
| **Realtime Service** | Node.js (Socket.IO) | 8088 | WebSocket updates |
| **Analytics Service** | Python (FastAPI) | 8089 | Data pipeline & reporting |

## Infrastructure Preservation

### Unchanged Components
- ✅ **Terraform configuration** (main.tf, variables.tf, outputs.tf)
- ✅ **EKS cluster setup** with Auto Mode
- ✅ **ArgoCD installation** and configuration
- ✅ **GitHub Actions workflow** (deploy.yml)
- ✅ **Helm chart structure** and patterns
- ✅ **ECR repositories** and image management
- ✅ **Ingress and networking** setup

### Minimal Changes Required
- 🔄 **Service names** in ArgoCD applications
- 🔄 **Helm chart values** for new service endpoints
- 🔄 **GitHub Actions matrix** to include new services
- 🔄 **README documentation** updates

## Implementation Strategy

### Step 1: Rename Existing Services
1. Update ArgoCD application names
2. Update Helm chart names and values
3. Update service discovery endpoints
4. Update GitHub Actions service matrix

### Step 2: Add New Services
1. Create new service directories following existing pattern
2. Add Dockerfiles and source code
3. Create Helm charts using existing templates
4. Add ArgoCD applications
5. Update GitHub Actions to include new services

### Step 3: Update Configuration
1. Update service-to-service communication endpoints
2. Configure event bus (Kafka) integration
3. Add database configurations (Postgres, Neo4j, Redis)
4. Update ingress routing

## Event-Driven Architecture

### Event Bus Integration
- **Kafka** for async communication
- **Event topics**: request.created, request.enriched, match.proposed, etc.
- **Service communication**: HTTP for sync, Kafka for async

### Data Stores
- **Request Service**: PostgreSQL
- **Volunteer Service**: PostgreSQL + Redis
- **Graph Service**: Neo4j
- **Matching Service**: Redis cache
- **NLP Service**: Model artifacts in S3
- **Analytics Service**: Data lake (S3) + ClickHouse

## Deployment Flow (Unchanged)

```mermaid
graph LR
    A[Code Push] --> B[GitHub Actions]
    B --> C[Build Images]
    C --> D[Push to ECR]
    D --> E[Update Helm Charts]
    E --> F[Commit Changes]
    F --> G[ArgoCD Sync]
    G --> H[Deploy to EKS]
```

## Benefits of This Approach

1. **Zero Infrastructure Changes**: Same Terraform, EKS, ArgoCD setup
2. **Proven CI/CD Pipeline**: Existing GitHub Actions workflow works unchanged
3. **Familiar Patterns**: Same Helm chart structure and deployment patterns
4. **Gradual Migration**: Can transform services one by one
5. **Operational Continuity**: Same monitoring, logging, and troubleshooting procedures

## Next Steps

1. Execute service renaming and transformation
2. Implement new services following existing patterns
3. Update documentation and configuration
4. Test end-to-end deployment pipeline
5. Validate ResQConnect functionality

This approach ensures minimal risk while leveraging the robust, production-ready infrastructure already in place.