variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Short resource name prefix"
  type        = string
  default     = "gobus"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "github_repo_url" {
  description = "HTTPS clone URL of the new PUBLIC GitHub repository"
  type        = string
}

variable "github_repository" {
  description = "GitHub owner/repository, e.g. myaccount/gobus"
  type        = string
}

variable "github_branch" {
  type    = string
  default = "main"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "ssh_ingress_cidrs" {
  description = "Optional SSH source CIDRs. Keep empty and use SSM if possible."
  type        = list(string)
  default     = []
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}
