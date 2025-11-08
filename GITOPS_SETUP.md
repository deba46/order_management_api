# GitOps Setup Guide

This repository follows a GitOps approach using GitHub Actions and ArgoCD.

## 🔄 CI/CD Flow

```
Code Push → GitHub Actions → Build & Test → Push to GHCR → Update Helm Values → ArgoCD Deploys
```

## 📋 Prerequisites

1. **GitHub Container Registry**
   - Enabled by default for GitHub repositories
   - Images pushed to: `ghcr.io/YOUR_USERNAME/YOUR_REPO_NAME`

2. **ArgoCD installed on your cluster**
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

3. **GitHub Secrets** (automatically available)
   - `GITHUB_TOKEN` - Provided by GitHub Actions

## 🚀 Setup Instructions

### 1. Update ArgoCD Application Manifest

Edit `argocd/application.yaml` and update:
```yaml
repoURL: https://github.com/YOUR_USERNAME/project_arculus.git
```

### 2. Make GitHub Container Registry Public (Optional)

For easier access without authentication:
- Go to your GitHub repository
- Navigate to Packages
- Find your container image
- Change visibility to Public

Or configure imagePullSecrets in Kubernetes.

### 3. Deploy ArgoCD Application

```bash
# Apply the ArgoCD application
kubectl apply -f argocd/application.yaml

# Check ArgoCD application status
kubectl get applications -n argocd

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Username: admin
# Get password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 4. Verify GitOps Flow

```bash
# Make a change and push to main branch
git add .
git commit -m "Test GitOps"
git push origin main

# Watch GitHub Actions
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# Watch ArgoCD sync
kubectl get application order-api -n argocd -w
```

## 🔧 How It Works

### GitHub Actions Pipeline

**On Push to `main` or `develop`:**

1. **Lint** - Code quality checks (flake8)
2. **Test** - Run unit tests with mocks
3. **Build & Push** - Build Docker image and push to GHCR with tags:
   - `main` (branch name)
   - `main-abc1234` (branch + short SHA)
   - `latest` (only for main branch)
4. **Update GitOps** - Updates `helm/order-api/values.yaml` with new image tag
5. **Commit Changes** - Pushes updated values back to repository

### ArgoCD

**Watches the repository and:**

1. **Detects Changes** - Monitors `helm/order-api/` directory
2. **Auto-Sync** - Automatically applies changes to cluster
3. **Self-Heal** - Reverts manual changes to match Git state
4. **Prune** - Removes resources no longer in Git

## 📊 Image Tags Strategy

| Trigger | Tags Generated | Example |
|---------|---------------|---------|
| Push to main | `latest`, `main`, `main-abc1234` | `ghcr.io/user/repo:main-abc1234` |
| Push to develop | `develop`, `develop-abc1234` | `ghcr.io/user/repo:develop-abc1234` |

The pipeline always uses the SHA-based tag in Helm values for precise versioning.

## 🔍 Monitoring

### Check Image in GHCR
```bash
# View packages
# Go to: https://github.com/YOUR_USERNAME?tab=packages
```

### Check ArgoCD Status
```bash
# CLI
kubectl get application order-api -n argocd
kubectl describe application order-api -n argocd

# UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open: https://localhost:8080
```

### Check Deployment
```bash
# Check pods
kubectl get pods -n orders-api

# Check current image
kubectl get deployment order-api -n orders-api -o jsonpath='{.spec.template.spec.containers[0].image}'

# View logs
kubectl logs -f deployment/order-api -n orders-api
```

## 🛠️ Manual Operations

### Force ArgoCD Sync
```bash
kubectl patch application order-api -n argocd --type merge -p '{"operation":{"sync":{}}}'
```

### Rollback to Previous Version
```bash
# Via ArgoCD UI or CLI
argocd app rollback order-api
```

### Update Configuration
1. Edit `helm/order-api/values.yaml`
2. Commit and push
3. ArgoCD will auto-sync

## 🔐 Security Best Practices

1. **Image Pull Secrets** (if using private registry)
   ```bash
   kubectl create secret docker-registry ghcr-secret \
     --docker-server=ghcr.io \
     --docker-username=YOUR_USERNAME \
     --docker-password=YOUR_PAT \
     --namespace=orders-api
   ```

2. **Sensitive Values** - Use sealed-secrets or external-secrets
3. **RBAC** - Configure ArgoCD RBAC for team access

## 📝 Workflow Files

- `.github/workflows/ci.yml` - Main CI/CD pipeline
- `argocd/application.yaml` - ArgoCD application definition
- `helm/order-api/` - Helm chart with templates and values

## 🎯 GitOps Principles Applied

✅ **Declarative** - All configs in Git
✅ **Versioned** - Git history tracks all changes
✅ **Immutable** - New images for every change
✅ **Automated** - CI/CD handles deployment
✅ **Self-healing** - ArgoCD maintains desired state
