# DevOps Guide — Yellow Pages Dashboard

Complete DevOps setup: CI/CD, containerization, reverse proxy, HTTPS,
monitoring, and Infrastructure as Code.

## Pipeline overview

```
push to GitHub -> GitHub Actions: lint -> test -> build image -> push to GHCR -> deploy to EC2
                                                                                      |
                                              nginx -> app -> MongoDB Atlas
                                              prometheus -> grafana (optional)
```

## FIRST: rotate the leaked database password

The old MongoDB URI (with password) was committed to a public repo and is in
git history. It is compromised.

1. MongoDB Atlas -> Database Access -> edit user -> set a NEW password.
2. Atlas -> Network Access -> remove 0.0.0.0/0; allow only your EC2 IP.
3. Put the new URI in `.env` on the server (never back in the code).

The app now reads `MONGODB_URI` from the environment and refuses to start
without it, so the secret never needs to live in the repo again.

## Required GitHub secrets

Settings -> Secrets and variables -> Actions:

| Secret        | Purpose                                        |
|---------------|------------------------------------------------|
| `EC2_HOST`    | Public IP / DNS of the EC2 host                |
| `EC2_USER`    | SSH user (e.g. root or ubuntu)                 |
| `EC2_SSH_KEY` | Private SSH key for the host                   |
| `GHCR_USER`   | GitHub username (for the EC2 to pull the image)|
| `GHCR_TOKEN`  | PAT with read:packages (or make image public)  |

`GITHUB_TOKEN` is automatic and pushes the image in CI.

## Local development

```
cp .env.example .env      # add your rotated MONGODB_URI
make install
make test
make run                  # http://localhost:8000
```

Ops endpoints: `/health` (liveness), `/ready` (DB check), `/metrics` (Prometheus).

## Deploy (on the EC2 host, one-time)

```
sudo mkdir -p /root/opt && cd /root/opt
git clone https://github.com/Zeeshan0335/yellowpages-dashboard.git
cd yellowpages-dashboard
cp .env.example .env      # add the rotated MONGODB_URI
```

After that, every push to main deploys automatically. Manual deploy:

```
docker compose pull && docker compose up -d
```

### Rollback

```
IMAGE=ghcr.io/zeeshan0335/yellowpages-dashboard:<old-sha> docker compose up -d
```

## HTTPS / SSL (Let's Encrypt)

1. Point a domain A record at the EC2 Elastic IP.
2. Set server_name in nginx/conf.d/app.conf to that domain.
3. Issue a cert:

```
docker run --rm -v certbot-conf:/etc/letsencrypt -v certbot-www:/var/www/certbot \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d dashboard.example.com --email you@example.com --agree-tos
```

4. Uncomment the 443 block in nginx/conf.d/app.conf, then restart nginx.

## Monitoring (Prometheus + Grafana)

```
make monitor
```

- Prometheus: http://<host>:9090
- Grafana:    http://<host>:3000 (admin / GRAFANA_ADMIN_PASSWORD)

## Infrastructure as Code (Terraform)

```
cd terraform
cp terraform.tfvars.example terraform.tfvars   # set key_name + your IP
terraform init
terraform plan
terraform apply
```

## File map

| Path                            | Purpose                                 |
|---------------------------------|-----------------------------------------|
| .github/workflows/ci-cd.yml     | lint -> test -> build -> push -> deploy |
| Dockerfile                      | Hardened image (non-root + healthcheck) |
| docker-compose.yml              | App + nginx (pulls image from registry) |
| docker-compose.monitoring.yml   | Prometheus + Grafana                    |
| nginx/conf.d/app.conf           | Reverse proxy + HTTPS-ready config      |
| monitoring/                     | Prometheus + Grafana provisioning       |
| terraform/                      | AWS infrastructure as code              |
| tests/                          | pytest suite (mongomock)                |
| .env.example                    | Secrets template (never commit .env)    |
| Makefile                        | Common dev/ops commands                 |
