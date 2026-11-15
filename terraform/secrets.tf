resource "random_password" "db" {
  length  = 28
  special = false
}

resource "random_password" "admin" {
  length  = 24
  special = false
}

resource "random_password" "flask" {
  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "app" {
  name                    = "${var.project_name}/application"
  recovery_window_in_days = 7
  tags                    = local.common_tags
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DB_HOST        = aws_db_instance.mysql.address
    DB_PORT        = "3306"
    DB_NAME        = "busbooking"
    DB_USER        = "busadmin"
    DB_PASSWORD    = random_password.db.result
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = random_password.admin.result
    SECRET_KEY     = random_password.flask.result
  })
}
