# GitHub Actions Secrets Setup

## Required Secrets for CI/CD

Add these to `Settings → Secrets and variables → Actions`:

### 1. ANTHROPIC_API_KEY
- Value: Your Anthropic API key from https://console.anthropic.com
- Used by: test.yml workflow
- Scope: Required for running tests that call Claude API

### 2. DOCKER_USERNAME (Optional)
- Value: Docker Hub username
- Used by: docker build/push workflows
- Scope: Only needed if pushing images to Docker Hub

### 3. DOCKER_PASSWORD (Optional)
- Value: Docker Hub access token (Settings → Security)
- Used by: docker build/push workflows
- Scope: Only needed if pushing images to Docker Hub

### 4. GKE_CLUSTER_NAME (Optional)
- Value: Your GKE cluster name
- Used by: deployment workflows
- Scope: Only needed if deploying to GKE

### 5. GKE_PROJECT_ID (Optional)
- Value: Your GCP project ID
- Used by: deployment workflows
- Scope: Only needed if deploying to GKE

## How to Add Secrets

1. Go to repo Settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Enter Name (e.g., `ANTHROPIC_API_KEY`)
5. Enter Value (e.g., `sk-ant-...`)
6. Click "Add secret"

## Using Secrets in Workflows

In .github/workflows/*.yml:
```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

Or in steps:
```yaml
- name: Run tests
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: pytest
```

## Security Best Practices

- Never log secrets (GitHub masks them automatically)
- Rotate API keys periodically
- Use separate keys for dev/staging/prod
- Audit secret access: Settings → Audit log
- Remove secrets if compromised: regenerate keys immediately

## Checking Secret Access

```bash
gh secret list  # List all secrets in repo
```

## Troubleshooting

- **Test fails with "auth error":** Verify ANTHROPIC_API_KEY is set correctly
- **Build fails silently:** Check "Actions" tab for workflow error messages
- **Secrets not available:** Wait 1 minute after adding, then re-run workflow
