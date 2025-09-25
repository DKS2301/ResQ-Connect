# =============================================================================
# IAM POLICIES FOR RESQCONNECT USER
# =============================================================================

# IAM policy for KMS permissions (if needed)
resource "aws_iam_policy" "resqconnect_kms_policy" {
  count       = 0  # Set to 1 if you need custom KMS permissions
  name        = "ResQConnect-KMS-Policy"
  description = "KMS permissions for ResQConnect EKS cluster"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Describe*",
          "kms:List*",
          "kms:GetKeyPolicy",
          "kms:GetKeyRotationStatus"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policy to user (if needed)
resource "aws_iam_user_policy_attachment" "resqconnect_kms_attach" {
  count      = 0  # Set to 1 if you need to attach the policy
  user       = "ResQConnect"
  policy_arn = aws_iam_policy.resqconnect_kms_policy[0].arn
}
