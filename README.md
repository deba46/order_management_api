# Order Management API

A FastAPI-based order management system with GitOps-driven CI/CD pipeline, deployed on Kubernetes.


## Features

- **RESTful API** - Full CRUD operations for order management
- **Health Monitoring** - Built-in health check endpoints for Kubernetes probes
- **Web Interface** - Simple UI for viewing and managing orders
- **PostgreSQL Database** - Production-grade relational database with connection pooling
- **Containerized Deployment** - Docker and Kubernetes-ready application
- **GitOps Workflow** - Automated deployments using ArgoCD
- **CI/CD Pipeline** - Automated testing, linting, and image building via GitHub Actions
- **Helm Charts** - Kubernetes manifests managed through Helm
- **Comprehensive Testing** - Unit and integration test suites with coverage reporting
- **Code Quality** - Automated linting with flake8
- **Monitoring** - Logging and monitoring with Grafana and Loki

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** 
- **[Uvicorn](https://www.uvicorn.org/)** 
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** 
- **[Jinja2](https://jinja.palletsprojects.com/)** 

### Database
- **[PostgreSQL](https://www.postgresql.org/)** 

### Infrastructure & Deployment
- **[Docker](https://www.docker.com/)** 
- **[Kubernetes](https://kubernetes.io/)** 
- **[Helm](https://helm.sh/)** 
- **[ArgoCD](https://argo-cd.readthedocs.io/)** 

### CI/CD & Monitoring
- **[GitHub Actions](https://github.com/features/actions)** 
- **[pytest](https://pytest.org/)**
- **[flake8](https://flake8.pycqa.org/)** 
- **[pytest-cov](https://pytest-cov.readthedocs.io/)** 

### Monitoring (Optional)
- **[Grafana](https://grafana.com/)** 

## CI/CD & GitOps Architecture

This project implements a complete GitOps workflow with automated continuous integration and deployment.

### Continuous Integration (GitHub Actions)
### Continuous Deployment (ArgoCD)
### GitOps Workflow Diagram

```
┌─────────────────┐
│  Code Changes   │
│  (Git Push)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│  CI Pipeline    │
│                 │
│ • Lint Code     │
│ • Unit Tests    │
│ • Integration   │
│   Tests (DB)    │
│ • Build Image   │
│ • Push to GHCR  │
│ • Update Helm   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Git Commit    │
│  (values.yaml)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     ArgoCD      │
│  (GitOps CD)    │
│                 │
│ • Detect Change │
│ • Sync Cluster  │
│ • Deploy App    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Kubernetes    │
│    Cluster      │
│  (Running App)  │
└─────────────────┘
```

## Getting Started

This guide will help you deploy the Order Management API in your local Kubernetes environment.

### Prerequisites

- Docker Desktop or Docker Engine
- kubectl CLI tool
- Helm 3.x
- Git

## Installation Guide

Follow these steps to set up the complete environment from scratch.

### Step 1: Clone the Repository

```bash
git clone https://github.com/deba46/order_management_api.git
cd order_management_api
```

### Step 2: Install Kind (Kubernetes in Docker)

Kind allows you to run a local Kubernetes cluster using Docker containers.

**On macOS:**
```bash
# Using Homebrew
brew install kind

# Or using Go
go install sigs.k8s.io/kind@latest
```

**On Linux:**
```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

**Verify installation:**
```bash
kind version
```

### Step 3: Create a Kind Cluster

```bash
# Create a cluster with ingress support
cat <<EOF | kind create cluster --name order-api-cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
```

**Verify cluster:**
```bash
kubectl cluster-info --context kind-order-api-cluster
kubectl get nodes
```

### Step 4: Install NGINX Ingress Controller

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

### Step 5: Create Self-Signed TLS Certificate

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /tmp/tls.key -out /tmp/tls.crt \
  -subj "/CN=order-api.local/O=order-api"

kubectl create secret tls order-api-tls \
  --cert=/tmp/tls.crt \
  --key=/tmp/tls.key \
  -n orders-api
```

### Step 6: Deploy PostgreSQL Database

```bash
# Create namespace
kubectl create namespace orders-api

# Apply PostgreSQL secret
kubectl apply -f k8s_manifests/database/postgresql-secret.yaml

# Deploy PostgreSQL StatefulSet
kubectl apply -f k8s_manifests/database/postgresql-statefulset.yaml

# Apply PostgreSQL Service
kubectl apply -f k8s_manifests/database/postgresql-service.yaml

```

### Step 7: Configure DNS (Update /etc/hosts)

Add a local DNS entry to map `order-api.local` to your localhost.

**On macOS/Linux:**
```bash
# Open /etc/hosts with sudo
sudo nano /etc/hosts

# Add this line at the end
127.0.0.1 order-api.local
```

**On Windows:**
```powershell
# Open as Administrator: C:\Windows\System32\drivers\etc\hosts
# Add this line:
127.0.0.1 order-api.local
```

**Save and exit** (Ctrl+O, Enter, Ctrl+X for nano)

### Step 8: Install the Application with Helm

```bash
# create ACR or github registry secret 
kubectl create secret docker-registry ghcr-secret --docker-server=ghcr.io --docker-username=deba46 --docker-password=<pat_token> -n orders-api
# Install the application using Helm
helm install order-api k8s_manifests/helm/order-api \
  --namespace orders-api 

# Verify deployment
kubectl get pods -n orders-api
kubectl get svc -n orders-api
kubectl get ingress -n orders-api
```
### Step 10: Verify the Deployment

```bash
# Check all resources
kubectl get all -n orders-api

# Check pod logs
kubectl logs -l app=order-api -n orders-api --tail=50

# Test the health endpoint
curl -k https://order-api.local/health
```

### Step 11: Install ArgoCD (For GitOps)

If you want to enable continuous deployment:

```bash
# Create ArgoCD namespace
kubectl create namespace argocd

helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd -n argocd 
# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
# Port-forward to use ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access ArgoCD UI at: https://localhost:8080
# Username: admin
# Password: (from command above)

# Deploy the application via ArgoCD
kubectl apply -f k8s_manifests/argocd/application.yaml
```

### Step 12: Access the Application

Open your browser and navigate to:

- **Application:** https://order-api.local
- **Health Check:** https://order-api.local/health
- **API Docs:** https://order-api.local/docs

**Note:** You'll see a browser warning about the self-signed certificate. Click "Advanced" and "Proceed to order-api.local" to continue.

### Step 13: Test the API

```bash
# Create an order
curl -k -X POST https://order-api.local/orders \
  -H "Content-Type: application/json" \
  -d '{"amount": 99.99}'

# Get all orders
curl -k https://order-api.local/orders

# Get specific order
curl -k https://order-api.local/orders/1
```

### Step 14: Install Grafana and Loki
``bash
kubectl create ns monitoring
kubectl apply -f k8s_manifests/grafana/grafana-datasource.yaml

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
# custom inputs 
helm upgrade --install loki grafana/loki-stack -n monitoring -f k8s_manifests/grafana/values.yaml
```

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Display orders web interface |
| GET | `/health` | Health check endpoint |
| POST | `/orders` | Create a new order |
| GET | `/orders` | Retrieve all orders |
| GET | `/orders/{id}` | Retrieve specific order by ID |

### Example Request

**Create Order:**
```bash
curl -X POST https://order-api.local/orders \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 149.99
  }'
```

**Response:**
```json
{
  "id": 1,
  "amount": 149.99,
  "created_at": "2025-11-09T10:30:00"
}
```

## Testing

### Run all tests

```bash
pytest tests/test_main.py -v
pytest tests/test_integration.py -v
pytest --cov=app --cov-report=html
```

## Linting
### Run flake8
```bash
flake8 app/ tests/
```
### Run pylint

```bash
pylint app/
```





