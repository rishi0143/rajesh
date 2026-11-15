# GoBus – Terraform + automatic deployment (AWS ap-south-1)

This starter provisions:
- VPC, public subnet, Internet Gateway and route table
- Two private subnets for RDS
- EC2 `t3.small` running Docker Compose
- Private RDS MySQL (`busbooking`)
- Secrets Manager secret for DB/admin/Flask credentials
- EC2 IAM role for Systems Manager and Secrets Manager
- GitHub Actions OIDC role for deployments through SSM (no SSH key)

## Before you start

1. Create a **new public GitHub repository** (example: `https://github.com/YOUR_GITHUB_USERNAME/gobus.git`).
   - Public is required by this starter because EC2 clones the repository without a GitHub token.
2. Copy your existing GoBus application files into the new repository root:
   - `app.py`, `database.py`, `requirements.txt`
   - `templates/`, `static/`
   - `Dockerfile`, `docker-compose.yml`
3. Copy your existing SQL schema to the repository root as `schema.sql` (from your old `terraform/schema.sql`).
4. Copy `app-files/Dockerfile` and `app-files/docker-compose.yml` into the new repository root (alongside `app.py`).
5. Ensure the repository root has a real `requirements.txt` (copy your existing one; `app-files/requirements.txt.example` is only a sample).
6. Add the `.github/workflows/deploy.yml` from this bundle.
7. Install Terraform, AWS CLI and configure AWS credentials with permission to create the resources in this project.

> Do not copy `admin.env`, `db.env`, `.env`, passwords, access keys or other secrets into GitHub.

## Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
- `github_repo_url`: full HTTPS clone URL of your new repository
- `github_repository`: `YOUR_GITHUB_USERNAME/YOUR_REPOSITORY`
- `ssh_ingress_cidr`: your public IP in CIDR form, e.g. `203.0.113.10/32`. SSH is optional and disabled by default (`[]`).

If you do not need SSH, leave `ssh_ingress_cidrs = []`. Use SSM for administration.

## Deploy

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Terraform creates a random database password, admin password and Flask secret key and stores them in Secrets Manager. It outputs the EC2 public IP and application URL.

First boot takes several minutes. Check:
```bash
terraform output
```
Open the `app_url` output from a phone or laptop. Nginx serves the app on port 80 and forwards requests internally to Flask/Gunicorn on localhost:5000.

To retrieve the generated admin login:
```bash
terraform output -raw admin_username
terraform output -raw admin_password
```
The password output is marked sensitive; keep it private. Do not paste it into chat or commit it to GitHub.

## Enable GitHub Actions auto-deploy

After `terraform apply`, add these to the new GitHub repository:

**Repository → Settings → Secrets and variables → Actions → Secrets**
- `AWS_DEPLOY_ROLE_ARN`: value from `terraform output -raw github_deploy_role_arn`

**Repository → Settings → Secrets and variables → Actions → Variables**
- `AWS_REGION`: `ap-south-1`
- `EC2_INSTANCE_ID`: value from `terraform output -raw ec2_instance_id`

Push to the `main` branch. The workflow assumes the AWS role using GitHub OIDC and asks SSM to run `/opt/gobus/deploy.sh` on EC2. No SSH private key is stored in GitHub.

## App / database requirements

- The Flask app must read `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SECRET_KEY`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` from environment variables.
- The app must listen on `0.0.0.0:5000`.
- The `schema.sql` file must create the tables expected by your current `database.py` and `app.py`.
- `docker-compose.yml` must define a service named `backend`, build from the repository root, load `admin.env` and `db.env`, and publish `5000:5000`.
- This starter imports `schema.sql` once during EC2 first boot if the file exists. Verify your schema matches your current app before production use.

## Important notes

- RDS is private; only the EC2 security group can connect to port 3306.
- The EC2 instance is public for website access. HTTP is enabled. For production, attach a domain and configure HTTPS with an ALB/ACM or a reverse proxy and certificate.
- AWS charges apply for EC2, RDS, storage, networking and Secrets Manager. Check the AWS Pricing Calculator.
- `terraform destroy` deletes infrastructure and can cause data loss. Back up the database first.
- This starter expects a new GitHub repository and does not create the GitHub repository itself.
