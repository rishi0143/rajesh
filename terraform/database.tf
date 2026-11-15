resource "aws_db_instance" "mysql" {
  identifier                 = "${var.project_name}-mysql"
  engine                     = "mysql"
  instance_class             = var.db_instance_class
  allocated_storage          = var.db_allocated_storage
  max_allocated_storage      = 50
  storage_type               = "gp3"
  storage_encrypted          = true
  db_name                    = "busbooking"
  username                   = "busadmin"
  password                   = random_password.db.result
  port                       = 3306
  db_subnet_group_name       = aws_db_subnet_group.main.name
  vpc_security_group_ids     = [aws_security_group.rds.id]
  publicly_accessible        = false
  multi_az                   = false
  backup_retention_period    = 1
  auto_minor_version_upgrade = true
  deletion_protection        = true
  skip_final_snapshot        = true
  apply_immediately          = true

  tags = merge(local.common_tags, { Name = "${var.project_name}-mysql" })
}
