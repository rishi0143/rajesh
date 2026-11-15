
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)

  common_tags = {
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}

# -------------------------
# VPC
# -------------------------
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-vpc"
  })
}

# -------------------------
# Internet Gateway
# -------------------------
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-igw"
  })
}

# -------------------------
# Public Subnet A
# -------------------------
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = local.azs[0]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name                                            = "${var.project_name}-public-a"
    "kubernetes.io/role/elb"                        = "1"
    "kubernetes.io/cluster/${var.project_name}-eks" = "shared"
  })
}

# -------------------------
# Private Database Subnet A
# -------------------------
resource "aws_subnet" "db_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = local.azs[0]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-private-db-a"
  })
}

# -------------------------
# Private Database Subnet B
# -------------------------
resource "aws_subnet" "db_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.12.0/24"
  availability_zone = local.azs[1]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-private-db-b"
  })
}

# -------------------------
# Public Route Table
# -------------------------
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-public-rt"
  })
}

# -------------------------
# Public Subnet A Route Association
# -------------------------
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# -------------------------
# RDS DB Subnet Group
# -------------------------
resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-db-subnets"

  subnet_ids = [
    aws_subnet.db_a.id,
    aws_subnet.db_b.id
  ]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-db-subnets"
  })
}
