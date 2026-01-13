# SpokeStack Deployment Guide

A step-by-step guide for deploying the SpokeStack multi-tenant AI agent platform. Written for beginners with clear explanations at each step.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick Start (Local Development)](#2-quick-start-local-development)
3. [Understanding the Architecture](#3-understanding-the-architecture)
4. [Docker Deployment](#4-docker-deployment)
5. [Cloud Deployment Options](#5-cloud-deployment-options)
6. [Kubernetes Deployment](#6-kubernetes-deployment)
7. [Configuration Reference](#7-configuration-reference)
8. [Post-Deployment Setup](#8-post-deployment-setup)
9. [Monitoring & Maintenance](#9-monitoring--maintenance)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

### What You Need

Before deploying SpokeStack, ensure you have:

| Requirement | Why You Need It | How to Get It |
|-------------|-----------------|---------------|
| **Anthropic API Key** | Powers all AI agents | Sign up at [console.anthropic.com](https://console.anthropic.com) |
| **Docker** | Runs the application in containers | [Install Docker](https://docs.docker.com/get-docker/) |
| **Git** | Download the code | [Install Git](https://git-scm.com/downloads) |

### Optional (for production)

| Requirement | Why You Need It | When Required |
|-------------|-----------------|---------------|
| **Kubernetes cluster** | Production orchestration | Kubernetes deployment |
| **Domain name** | Public access | Production deployment |
| **SSL certificate** | Secure connections (HTTPS) | Production deployment |

### Verify Your Setup

Open a terminal and run these commands:

```bash
# Check Docker is installed
docker --version
# Expected: Docker version 24.x.x or higher

# Check Docker Compose is installed
docker compose version
# Expected: Docker Compose version v2.x.x or higher

# Check Git is installed
git --version
# Expected: git version 2.x.x or higher
```

---

## 2. Quick Start (Local Development)

**Time required: ~10 minutes**

This gets SpokeStack running on your local machine for testing.

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/ongoing_agent_builder.git

# Enter the directory
cd ongoing_agent_builder
```

### Step 2: Create Environment File

Create a file named `.env` in the project root:

```bash
# Create the .env file
cat > .env << 'EOF'
# Required: Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Optional: ERP integration (leave empty if not using)
ERP_API_BASE_URL=
ERP_API_KEY=

# Service configuration (defaults are fine for local dev)
SERVICE_PORT=8000
LOG_LEVEL=INFO
EOF
```

**Important:** Replace `sk-ant-your-api-key-here` with your actual Anthropic API key.

### Step 3: Start the Services

```bash
# Start all services (database, redis, app)
docker compose up -d

# Wait for services to be healthy (~30 seconds)
docker compose ps
```

You should see output like:
```
NAME                  STATUS    PORTS
spokestack-agents     running   0.0.0.0:8000->8000/tcp
spokestack-postgres   running   0.0.0.0:5432->5432/tcp
spokestack-redis      running   0.0.0.0:6379->6379/tcp
```

### Step 4: Run Database Migrations

```bash
# Run migrations to create database tables
docker compose run --rm migrations
```

### Step 5: Verify It's Working

Open your browser and go to: **http://localhost:8000**

You should see:
```json
{
  "service": "SpokeStack Agent Service",
  "version": "1.0.0",
  "paradigm": "Think → Act → Create",
  "docs": "/docs"
}
```

Visit **http://localhost:8000/docs** for the interactive API documentation.

### Step 6: Test an Agent

Using the API docs at `/docs`, or with curl:

```bash
# Create your first instance (tenant)
curl -X POST http://localhost:8000/api/v1/instances \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Agency",
    "slug": "my-agency",
    "organization_name": "My Agency Inc"
  }'
```

You'll get back an instance ID. Use it to execute an agent:

```bash
# Execute an agent (replace INSTANCE_ID with the ID from above)
curl -X POST http://localhost:8000/api/v1/instances/INSTANCE_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "copy",
    "task": "Write a tagline for a coffee shop called Morning Brew",
    "user_id": "test-user"
  }'
```

### Stopping the Services

```bash
# Stop all services
docker compose down

# Stop and remove all data (fresh start)
docker compose down -v
```

---

## 3. Understanding the Architecture

### How SpokeStack Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your Requests                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SpokeStack Agent Service                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ API Routes  │→ │AgentFactory │→ │ 46 AI Agents            │  │
│  │             │  │             │  │ (Copy, Media Buying...) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                          │                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │PromptAssemb │  │SkillExecutor│  │ FeedbackAnalyzer        │  │
│  │ler (3-tier) │  │ (webhooks)  │  │ (auto-learning)         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │     Redis       │  │  Claude API     │
│   (Data Store)  │  │  (Task Queue)   │  │  (AI Engine)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Three-Layer Architecture

SpokeStack uses three layers for flexibility:

| Layer | What It Contains | How It's Updated |
|-------|------------------|------------------|
| **Layer 1: Core Agents** | 46 pre-built AI agents | Code deployment |
| **Layer 2: Instance Config** | Per-tenant settings | Database (hot-reload) |
| **Layer 3: Custom Skills** | Webhook-based extensions | Database (instant) |

### Three-Tier Tuning

Each agent's behavior can be customized at three levels:

| Tier | Who Controls It | Examples |
|------|-----------------|----------|
| **Tier 1: Platform** | SpokeStack team | Safety rules, base prompts |
| **Tier 2: Instance** | Agency admins | Industry knowledge, agency voice |
| **Tier 3: Client** | Account managers | Brand voice, content rules |

---

## 4. Docker Deployment

### For Development

Already covered in [Quick Start](#2-quick-start-local-development).

### For Staging/Production

Use the production override file for better performance:

```bash
# Set production environment variables
export VERSION=1.0.0
export DB_PASSWORD=your-secure-password-here

# Start with production settings
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

This gives you:
- 3 replicas of the agent service
- Resource limits
- Better logging
- Restart policies

---

## 5. Cloud Deployment Options

### Option A: Railway (Easiest)

**Time: ~15 minutes | Cost: ~$5-20/month**

[Railway](https://railway.app) handles everything for you.

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add PostgreSQL**
   - In your project, click "+ New"
   - Select "Database" → "PostgreSQL"

4. **Add Redis**
   - Click "+ New"
   - Select "Database" → "Redis"

5. **Configure Environment**
   - Click on your service
   - Go to "Variables"
   - Add:
     ```
     ANTHROPIC_API_KEY=sk-ant-your-key
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     REDIS_URL=${{Redis.REDIS_URL}}
     ```

6. **Deploy**
   - Railway auto-deploys on push
   - Your service URL appears in the dashboard

### Option B: Render

**Time: ~20 minutes | Cost: ~$7-25/month**

1. Go to [render.com](https://render.com)
2. Create a "Web Service" from your repo
3. Add a PostgreSQL database
4. Add a Redis instance
5. Connect them via environment variables

### Option C: AWS (Most Control)

**Time: ~1-2 hours | Cost: Varies**

Use AWS services:
- **ECS Fargate** or **EKS** for containers
- **RDS** for PostgreSQL
- **ElastiCache** for Redis
- **ALB** for load balancing

See [Kubernetes Deployment](#6-kubernetes-deployment) for EKS setup.

### Option D: Google Cloud

**Time: ~1-2 hours | Cost: Varies**

Use GCP services:
- **Cloud Run** or **GKE** for containers
- **Cloud SQL** for PostgreSQL
- **Memorystore** for Redis

---

## 6. Kubernetes Deployment

For production deployments with full control.

### Prerequisites

- Kubernetes cluster (EKS, GKE, AKS, or self-managed)
- `kubectl` configured to access your cluster
- Container registry (Docker Hub, ECR, GCR)

### Step 1: Build and Push Image

```bash
# Build the image
docker build -t spokestack-agents:1.0.0 .

# Tag for your registry (example: Docker Hub)
docker tag spokestack-agents:1.0.0 your-registry/spokestack-agents:1.0.0

# Push to registry
docker push your-registry/spokestack-agents:1.0.0
```

### Step 2: Update Kubernetes Manifests

Edit `k8s/deployment.yaml` to use your image:

```yaml
image: your-registry/spokestack-agents:1.0.0
```

### Step 3: Configure Secrets

**Important:** Never commit real secrets to Git!

```bash
# Create the Anthropic API key secret
kubectl create secret generic spokestack-secrets \
  --namespace=spokestack \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-your-actual-key \
  --from-literal=DB_PASSWORD=your-secure-db-password
```

Or update `k8s/secret.yaml` with base64-encoded values:

```bash
# Encode your API key
echo -n "sk-ant-your-actual-key" | base64
# Use this output in secret.yaml
```

### Step 4: Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configuration
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy database and cache
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=postgres -n spokestack --timeout=120s

# Run migrations
kubectl apply -f k8s/migrations-job.yaml
kubectl wait --for=condition=complete job/spokestack-migrations -n spokestack --timeout=120s

# Deploy the agent service
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# (Optional) Deploy ingress for external access
kubectl apply -f k8s/ingress.yaml

# (Optional) Deploy autoscaler
kubectl apply -f k8s/hpa.yaml
```

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n spokestack

# Check services
kubectl get svc -n spokestack

# View logs
kubectl logs -f deployment/spokestack-agents -n spokestack

# Test health endpoint
kubectl port-forward svc/spokestack-agents 8000:80 -n spokestack
# Then visit http://localhost:8000/health
```

### Step 6: Access Your Deployment

**Option A: Port Forward (Testing)**
```bash
kubectl port-forward svc/spokestack-agents 8000:80 -n spokestack
# Access at http://localhost:8000
```

**Option B: LoadBalancer (Cloud)**
```bash
# Change service type to LoadBalancer
kubectl patch svc spokestack-agents -n spokestack -p '{"spec": {"type": "LoadBalancer"}}'

# Get external IP
kubectl get svc spokestack-agents -n spokestack
```

**Option C: Ingress (Recommended)**
Configure your domain in `k8s/ingress.yaml` and apply.

---

## 7. Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | **Yes** | - | Your Anthropic API key |
| `DATABASE_URL` | **Yes** | - | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection string |
| `CLAUDE_MODEL` | No | `claude-opus-4-5-20250514` | Claude model to use |
| `SERVICE_PORT` | No | `8000` | Port to listen on |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `ERP_API_BASE_URL` | No | - | ERP integration URL |
| `ERP_API_KEY` | No | - | ERP API key |

### Database URL Format

```
postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
```

Examples:
```bash
# Local
DATABASE_URL=postgresql+asyncpg://spokestack:spokestack@localhost:5432/spokestack

# AWS RDS
DATABASE_URL=postgresql+asyncpg://admin:password@mydb.xxx.us-east-1.rds.amazonaws.com:5432/spokestack

# Railway (auto-configured)
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

---

## 8. Post-Deployment Setup

### Create Your First Instance

After deployment, create an instance for your organization:

```bash
curl -X POST https://your-domain.com/api/v1/instances \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Agency Name",
    "slug": "your-agency",
    "organization_name": "Your Agency Inc",
    "contact_email": "admin@youragency.com",
    "tier": "enterprise"
  }'
```

### Add a Client

```bash
curl -X POST https://your-domain.com/api/v1/instances/INSTANCE_ID/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "slug": "acme",
    "industry": "Technology",
    "vertical": "SaaS"
  }'
```

### Configure Instance Tuning

```bash
curl -X PUT https://your-domain.com/api/v1/instances/INSTANCE_ID/tuning \
  -H "Content-Type: application/json" \
  -d '{
    "agency_brand_voice": "Professional yet approachable...",
    "vertical_knowledge": "Expertise in B2B SaaS marketing...",
    "behavior_params": {
      "creativity_level": "balanced",
      "formality": "professional"
    }
  }'
```

### Add a Custom Skill (Optional)

```bash
curl -X POST https://your-domain.com/api/v1/instances/INSTANCE_ID/skills \
  -H "Content-Type: application/json" \
  -d '{
    "name": "check_brand_guidelines",
    "description": "Validates content against brand guidelines stored in our system",
    "input_schema": {
      "type": "object",
      "properties": {
        "content": {"type": "string", "description": "Content to validate"}
      },
      "required": ["content"]
    },
    "webhook_url": "https://your-api.com/brand-check",
    "webhook_auth": {
      "type": "bearer",
      "token": "your-api-token"
    }
  }'
```

---

## 9. Monitoring & Maintenance

### Health Checks

The service exposes these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Basic health check (for load balancers) |
| `GET /` | Service info |
| `GET /docs` | API documentation |

### Viewing Logs

**Docker:**
```bash
docker compose logs -f agents
```

**Kubernetes:**
```bash
kubectl logs -f deployment/spokestack-agents -n spokestack
```

### Database Backups

**Docker:**
```bash
# Create backup
docker exec spokestack-postgres pg_dump -U spokestack spokestack > backup.sql

# Restore backup
docker exec -i spokestack-postgres psql -U spokestack spokestack < backup.sql
```

**Kubernetes:**
```bash
# Create backup
kubectl exec -n spokestack spokestack-postgres-0 -- pg_dump -U spokestack spokestack > backup.sql
```

### Updating the Service

**Docker:**
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose build
docker compose up -d
```

**Kubernetes:**
```bash
# Build new image
docker build -t your-registry/spokestack-agents:1.0.1 .
docker push your-registry/spokestack-agents:1.0.1

# Update deployment
kubectl set image deployment/spokestack-agents \
  agents=your-registry/spokestack-agents:1.0.1 \
  -n spokestack
```

---

## 10. Troubleshooting

### Common Issues

#### "Connection refused" to database

**Problem:** App can't connect to PostgreSQL.

**Solution:**
```bash
# Check if postgres is running
docker compose ps postgres

# Check postgres logs
docker compose logs postgres

# Verify connection string
docker compose exec agents env | grep DATABASE
```

#### "Invalid API key" from Claude

**Problem:** Anthropic API key is invalid or not set.

**Solution:**
```bash
# Check if key is set
docker compose exec agents env | grep ANTHROPIC

# Verify key format (should start with sk-ant-)
echo $ANTHROPIC_API_KEY
```

#### Migrations fail

**Problem:** `alembic upgrade head` fails.

**Solution:**
```bash
# Check database is accessible
docker compose exec agents python -c "from src.db.session import engine; print('OK')"

# Run migrations with verbose output
docker compose exec agents alembic upgrade head --sql
```

#### Out of memory

**Problem:** Container keeps restarting with OOM errors.

**Solution:**
```bash
# Increase memory limits in docker-compose.yml
# Or in Kubernetes deployment.yaml
resources:
  limits:
    memory: "8Gi"  # Increase as needed
```

### Getting Help

1. **Check logs first** - Most issues are visible in logs
2. **Verify environment** - Double-check all required environment variables
3. **Test components** - Test database and Redis connections independently
4. **API Documentation** - Visit `/docs` for endpoint details

---

## Quick Reference

### Start Everything
```bash
docker compose up -d
```

### Stop Everything
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f
```

### Run Migrations
```bash
docker compose run --rm migrations
```

### Access Shell
```bash
docker compose exec agents bash
```

### Test Health
```bash
curl http://localhost:8000/health
```

---

**Congratulations!** You've deployed SpokeStack. Visit `/docs` to explore the API and start building with AI agents.
