output "app_url" {
  value       = "http://${aws_instance.app.public_ip}"
  description = "Open this URL on mobile or laptop"
}

output "ec2_public_ip" {
  value = aws_instance.app.public_ip
}

output "ec2_instance_id" {
  value = aws_instance.app.id
}

output "rds_endpoint" {
  value = aws_db_instance.mysql.address
}

output "admin_username" {
  value = "admin"
}

output "admin_password" {
  value     = random_password.admin.result
  sensitive = true
}

output "github_deploy_role_arn" {
  value = aws_iam_role.github_deploy.arn
}
output "eks_cluster_name" {
  value = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "eks_node_group_name" {
  value = aws_eks_node_group.main.node_group_name
}

output "eks_node_role_arn" {
  value = aws_iam_role.eks_nodes.arn
}

output "ecr_backend_url" {
  value = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  value = aws_ecr_repository.frontend.repository_url
}