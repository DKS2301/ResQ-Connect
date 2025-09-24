# ResQConnect Deployment Guide

## 🚀 Complete Deployment Instructions

### Prerequisites
- AWS CLI configured with appropriate credentials
- Terraform >= 1.0 installed
- kubectl installed
- Docker installed (for local testing)
- GitHub repository with secrets configured

### Required GitHub Secrets
Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

| Secret Name             | Description    | Example        |
| ----------------------- | -------------- | -------------- |
| `AWS_ACCESS_KEY_ID`     | AWS Access Key | `AKIA...`      |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key | `wJalrXUt...`  |
| `AWS_REGION`            | AWS Region     | `us-west-2`    |
| `AWS_ACCOUNT_ID`        | AWS Account ID | `123456789012` |

## 📋 Deployment Steps

### Step 1: Infrastructure Deployment

```bash
# Clone the repository
git clone <your-repo-url>
cd resqconnect-platform
git checkout gitops

# Navigate to terraform directory
cd terraform/

# Initialize Terraform
terraform init

# Deploy EKS cluster and VPC (Phase 1)
terraform apply -target=module.retail_app_eks -target=module.vpc --auto-approve
```

**⏱️ Expected time: 15-20 minutes**

### Step 2: Configure kubectl

```bash
# Get cluster name (with random suffix)
terraform output cluster_name

# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name $(terraform output -raw cluster_name)

# Verify connection
kubectl get nodes
```

### Step 3: Deploy ArgoCD and Applications

```bash
# Deploy ArgoCD and add-ons (Phase 2)
terraform apply --auto-approve
```

**⏱️ Expected time: 5-10 minutes**

### Step 4: Verify ArgoCD Installation

```bash
# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d

# Port-forward to ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 9090:443 &

# Access: https://localhost:9090
# Username: admin
# Password: (from above command)
```

### Step 5: Deploy ResQConnect Services

```bash
# Push code to trigger CI/CD pipeline
git add .
git commit -m "Deploy ResQConnect platform"
git push origin gitops
```

The GitHub Actions workflow will automatically:
1. Detect changed services
2. Build Docker images
3. Push to ECR
4. Update Helm chart values
5. Commit changes
6. ArgoCD will sync and deploy

### Step 6: Access the Application

```bash
# Get load balancer URL
kubectl get svc -n ingress-nginx

# Check application status
kubectl get pods -n resqconnect
kubectl get svc -n resqconnect
```

## 🔍 Verification Commands

### Check All Services
```bash
# Check ArgoCD applications
kubectl get applications -n argocd

# Check ResQConnect pods
kubectl get pods -n resqconnect

# Check services
kubectl get svc -n resqconnect

# Check ingress
kubectl get ingress -n resqconnect
```

### Service Health Checks
```bash
# Port-forward to test services locally
kubectl port-forward -n resqconnect svc/resqconnect-coordinator-ui 8080:80 &
kubectl port-forward -n resqconnect svc/resqconnect-request-service 8081:80 &
kubectl port-forward -n resqconnect svc/resqconnect-volunteer-service 8082:80 &
kubectl port-forward -n resqconnect svc/resqconnect-matching-service 8083:80 &
kubectl port-forward -n resqconnect svc/resqconnect-notification-service 8084:80 &
kubectl port-forward -n resqconnect svc/resqconnect-ingest-service 8085:80 &
kubectl port-forward -n resqconnect svc/resqconnect-nlp-service 8086:80 &
kubectl port-forward -n resqconnect svc/resqconnect-graph-service 8087:80 &
kubectl port-forward -n resqconnect svc/resqconnect-realtime-service 8088:80 &
kubectl port-forward -n resqconnect svc/resqconnect-analytics-service 8089:80 &

# Test health endpoints
curl http://localhost:8080/health  # Coordinator UI
curl http://localhost:8081/health  # Request Service
curl http://localhost:8082/health  # Volunteer Service
curl http://localhost:8083/health  # Matching Service
curl http://localhost:8084/health  # Notification Service
curl http://localhost:8085/health  # Ingest Service
curl http://localhost:8086/health  # NLP Service
curl http://localhost:8087/api/graph/health  # Graph Service
curl http://localhost:8088/health  # Realtime Service
curl http://localhost:8089/health  # Analytics Service
```

## 🔧 Troubleshooting

### Common Issues

#### 1. ArgoCD Applications Not Syncing
```bash
# Check ArgoCD logs
kubectl logs -n argocd deployment/argocd-application-controller
kubectl logs -n argocd deployment/argocd-server

# Force sync an application
kubectl patch application resqconnect-coordinator-ui -n argocd --type merge -p '{"operation":{"sync":{"syncStrategy":{"hook":{"force":true}}}}}'
```

#### 2. Pods Not Starting
```bash
# Check pod logs
kubectl logs -n resqconnect deployment/resqconnect-coordinator-ui
kubectl describe pod -n resqconnect <pod-name>

# Check events
kubectl get events -n resqconnect --sort-by='.lastTimestamp'
```

#### 3. Service Discovery Issues
```bash
# Check service endpoints
kubectl get endpoints -n resqconnect

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm -- /bin/sh
# Inside the pod:
nslookup resqconnect-request-service.resqconnect.svc.cluster.local
```

#### 4. GitHub Actions Failing
- Check AWS credentials in GitHub secrets
- Verify ECR repository permissions
- Check workflow logs in GitHub Actions tab

### Monitoring and Logs

```bash
# Check all resources
kubectl get all -n resqconnect

# Monitor ArgoCD sync status
kubectl get applications -n argocd -w

# Check ingress controller
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

## 🧹 Cleanup

### Destroy Infrastructure
```bash
cd terraform/

# Option 1: Destroy everything at once
terraform destroy --auto-approve

# Option 2: Destroy in phases (recommended)
terraform destroy -target=module.eks_addons --auto-approve
terraform destroy -target=module.retail_app_eks --auto-approve
terraform destroy --auto-approve
```

### Clean Up ECR Repositories
```bash
# Delete ECR repositories
aws ecr delete-repository --repository-name resqconnect-coordinator-ui --force
aws ecr delete-repository --repository-name resqconnect-request-service --force
aws ecr delete-repository --repository-name resqconnect-volunteer-service --force
aws ecr delete-repository --repository-name resqconnect-matching-service --force
aws ecr delete-repository --repository-name resqconnect-notification-service --force
aws ecr delete-repository --repository-name resqconnect-ingest-service --force
aws ecr delete-repository --repository-name resqconnect-nlp-service --force
aws ecr delete-repository --repository-name resqconnect-graph-service --force
aws ecr delete-repository --repository-name resqconnect-realtime-service --force
aws ecr delete-repository --repository-name resqconnect-analytics-service --force
```

## 📊 Service Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Victims       │    │  Volunteers     │    │  Coordinators   │
│                 │    │                 │    │                 │
│ SMS/WhatsApp    │    │ Mobile App      │    │ Web Dashboard   │
│ Web Forms       │    │ Push Notifs     │    │ Real-time View  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Ingress                        │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ResQConnect Services                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Ingest    │  │     NLP     │  │   Request   │             │
│  │   Service   │→ │   Service   │→ │   Service   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                           │                     │
│  ┌─────────────┐  ┌─────────────┐       ▼                     │
│  │ Volunteer   │  │   Graph     │  ┌─────────────┐             │
│  │  Service    │→ │  Service    │← │  Matching   │             │
│  └─────────────┘  └─────────────┘  │   Service   │             │
│                                    └─────────────┘             │
│  ┌─────────────┐  ┌─────────────┐       │                     │
│  │ Realtime    │  │Notification │←──────┘                     │
│  │  Service    │  │  Service    │                             │
│  └─────────────┘  └─────────────┘                             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐                             │
│  │ Analytics   │  │Coordinator  │                             │
│  │  Service    │  │     UI      │                             │
│  └─────────────┘  └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Data Layer (PostgreSQL, Neo4j, Redis)             │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Success Metrics

After successful deployment, you should see:

- ✅ All 10 ResQConnect services running
- ✅ ArgoCD applications in sync
- ✅ Health endpoints responding
- ✅ Load balancer accessible
- ✅ Real-time WebSocket connections working
- ✅ Event-driven communication between services
- ✅ Monitoring and metrics collection active

## 🔄 Making Changes

To update any service:

1. Make code changes in the respective `src/<service>/` directory
2. Commit and push to the `gitops` branch
3. GitHub Actions will automatically build and deploy
4. ArgoCD will sync the changes to the cluster

The platform is now ready for disaster relief operations! 🚀