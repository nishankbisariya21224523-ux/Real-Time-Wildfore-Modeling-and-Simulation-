# Production Deployment Guide

## 1. Overview

This guide provides instructions for deploying the Forest Fire Prediction and Spread Simulation Platform in staging and production environments.

The platform architecture comprises:
- **Web Frontend**: React 18 + TypeScript SPA served via Nginx or static CDN.
- **Backend API**: FastAPI running behind Uvicorn/Gunicorn.
- **Background Worker**: Celery worker executing spread simulation tasks.
- **Database**: PostgreSQL 16 with PostGIS 3.4 spatial extension.
- **Task Broker & Cache**: Redis 7.

---

## 2. Infrastructure Prerequisites

| Component | Minimum Specification | Recommended Production |
|---|---|---|
| **CPU** | 4 Cores (x86_64) | 8–16 Cores |
| **RAM** | 8 GB | 16–32 GB |
| **Disk Space** | 40 GB SSD | 200+ GB NVMe SSD |
| **OS** | Ubuntu 22.04 LTS / Debian 12 | Ubuntu 24.04 LTS / RHEL 9 |
| **Container Engine** | Docker 24.0+ & Docker Compose v2.20+ | Kubernetes 1.28+ or Docker Swarm |

---

## 3. Deployment Option A: Docker Compose (Single VM / Node)

### Step 1: Clone Repository & Configure Environment
```bash
git clone https://github.com/organization/forest-fire-platform.git
cd forest-fire-platform

# Create production environment configuration from template
cp .env.production.example .env.production

# Generate secure 32-byte secret key and update passwords
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/CHANGE_ME_IN_PRODUCTION_USE_MINIMUM_32_CHARACTERS_HEX_KEY/$SECRET_KEY/g" .env.production
```

Edit `.env.production` to provide strong database and Redis credentials:
```bash
nano .env.production
```

### Step 2: Build & Start Containerized Services
```bash
docker compose --env-file .env.production build
docker compose --env-file .env.production up -d
```

### Step 3: Run Database Migrations & Seed Data
```bash
# Execute Alembic migrations
docker compose --env-file .env.production exec api alembic upgrade head

# Seed reference monitoring regions and spatial geometries
docker compose --env-file .env.production exec api python database/seed/seed_regions.py
```

### Step 4: Verify Service Health
```bash
curl -f http://localhost:8000/api/v1/health
```
Expected output:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0"
}
```

---

## 4. Deployment Option B: Distributed / Bare-Metal Deployment

### 4.1 Database Layer (PostgreSQL + PostGIS)
```bash
sudo apt update && sudo apt install -y postgresql-16 postgresql-16-postgis-3
sudo -u postgres psql -c "CREATE USER forest_admin WITH PASSWORD 'StrongPasswordHere';"
sudo -u postgres psql -c "CREATE DATABASE forest_fire_db OWNER forest_admin;"
sudo -u postgres psql -d forest_fire_db -c "CREATE EXTENSION postgis;"
```

### 4.2 Redis Server
```bash
sudo apt install -y redis-server
sudo systemctl enable --now redis-server
```

### 4.3 Backend API & Celery Service
Install system dependencies and python environment:
```bash
sudo apt install -y python3.11 python3.11-venv libgdal-dev
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r services/api/requirements.txt
pip install -r services/risk-engine/requirements.txt
pip install -r services/spread-engine/requirements.txt
```

Run database migrations:
```bash
alembic upgrade head
python database/seed/seed_regions.py
```

Configure Systemd service for FastAPI (`/etc/systemd/system/forest-fire-api.service`):
```ini
[Unit]
Description=Forest Fire Prediction API
After=network.target postgresql.service redis.service

[Service]
User=www-data
WorkingDirectory=/opt/forest-fire-platform
EnvironmentFile=/opt/forest-fire-platform/.env.production
ExecStart=/opt/forest-fire-platform/.venv/bin/uvicorn services.api.app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Configure Systemd service for Celery Worker (`/etc/systemd/system/forest-fire-celery.service`):
```ini
[Unit]
Description=Forest Fire Celery Spread Simulation Worker
After=network.target redis.service

[Service]
User=www-data
WorkingDirectory=/opt/forest-fire-platform
EnvironmentFile=/opt/forest-fire-platform/.env.production
ExecStart=/opt/forest-fire-platform/.venv/bin/celery -A services.api.app.celery_app worker --loglevel=info --concurrency=4
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4.4 Frontend Static Build & Nginx
```bash
cd apps/web
npm ci
npm run build
```

Nginx configuration (`/etc/nginx/sites-available/forest-fire.conf`):
```nginx
server {
    listen 80;
    server_name fire-platform.example.gov.in;

    root /opt/forest-fire-platform/apps/web/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 5. Health Checks & Verification Runbook

1. Check HTTP Liveness: `curl http://<host>:8000/api/v1/health`
2. Check Regions Endpoint: `curl http://<host>:8000/api/v1/regions`
3. Check Active Fire Hotspots: `curl http://<host>:8000/api/v1/fires/active`
4. Inspect Celery Worker status: `celery -A services.api.app.celery_app inspect ping`
