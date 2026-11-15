

# --------------------------------
# ECR BACKEND REPOSITORY
# --------------------------------

resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

# --------------------------------
# ECR FRONTEND REPOSITORY
# --------------------------------

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.project_name}-frontend"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

# --------------------------------
# GITHUB ACTIONS ECR PUSH PERMISSIONS
# --------------------------------

resource "aws_iam_role_policy" "github_ecr_push" {
  name = "${var.project_name}-github-ecr-push"
  role = aws_iam_role.github_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ecr:GetAuthorizationToken"
        ]

        Resource = "*"
      },
      {
        Effect = "Allow"

        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:CompleteLayerUpload",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:PutImage",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]

        Resource = [
          aws_ecr_repository.backend.arn,
          aws_ecr_repository.frontend.arn
        ]
      }
    ]
  })
}

# --------------------------------
# GITHUB ACTIONS EKS DESCRIBE ACCESS
# --------------------------------

resource "aws_iam_role_policy" "github_eks_access" {
  name = "${var.project_name}-github-eks-access"
  role = aws_iam_role.github_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Action = [
        "eks:DescribeCluster"
      ]

      Resource = aws_eks_cluster.main.arn
    }]
  })
}
