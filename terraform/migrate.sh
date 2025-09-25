#!/bin/bash

# =============================================================================
# RESQCONNECT MIGRATION SCRIPT
# =============================================================================

set -e

echo "🚀 Starting ResQConnect infrastructure migration..."

# Step 1: Destroy old retail-store infrastructure
echo "📋 Step 1: Destroying old retail-store infrastructure..."
terraform destroy -auto-approve || echo "⚠️  Some resources may have already been destroyed"

# Step 2: Clean up state
echo "📋 Step 2: Cleaning up Terraform state..."
rm -f terraform.tfstate*
rm -f tfplan

# Step 3: Reinitialize Terraform
echo "📋 Step 3: Reinitializing Terraform..."
terraform init -upgrade

# Step 4: Plan new infrastructure
echo "📋 Step 4: Planning new ResQConnect infrastructure..."
terraform plan -out=tfplan

# Step 5: Apply new infrastructure
echo "📋 Step 5: Applying new ResQConnect infrastructure..."
terraform apply tfplan

echo "✅ Migration completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update kubeconfig: aws eks update-kubeconfig --region us-west-2 --name \$(terraform output -raw cluster_name)"
echo "2. Verify cluster: kubectl get nodes"
echo "3. Check ArgoCD: kubectl get pods -n argocd"
echo ""
echo "🎉 ResQConnect infrastructure is ready!"
