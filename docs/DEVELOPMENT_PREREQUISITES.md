# Development Prerequisites

## Before Running `make setup`

Ensure you have these installed:

### Required

- **Python 3.13+**
  ```bash
  python3 --version  # Should be 3.13 or higher
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

- **Docker & Docker Compose**
  ```bash
  docker --version
  docker-compose --version
  ```

- **Git**
  ```bash
  git --version
  ```

### Optional but Recommended

- **kubectl** (for K8s deployments)
  ```bash
  kubectl version --client
  ```

- **helm** (for K8s Helm charts)
  ```bash
  helm version
  ```

- **k6** (for load testing)
  ```bash
  k6 version
  ```

- **PostgreSQL CLI** (for direct DB access)
  ```bash
  psql --version
  ```

## Installation (macOS)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.13 docker docker-compose git kubectl helm k6 postgresql@16

# Start Docker daemon
open /Applications/Docker.app
```

## Installation (Linux - Ubuntu/Debian)

```bash
# Update package manager
sudo apt-get update

# Install Python 3.13
sudo apt-get install python3.13 python3-pip

# Install Docker
sudo apt-get install docker.io docker-compose

# Install kubectl
curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install k6
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3232A
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## Verification

After installation, verify everything works:

```bash
# Check all tools are installed
python3 --version
pip --version
docker --version
git --version

# Verify you can connect to Docker
docker run hello-world

# Now run setup
make setup
```

## Troubleshooting

### "python3 not found"
- Ensure Python 3.13+ is in your PATH
- Try `python --version` if `python3` doesn't work
- Reinstall Python if necessary

### "docker not found"
- Ensure Docker Desktop (Mac/Windows) is running
- On Linux, ensure docker daemon is running: `sudo systemctl start docker`

### "permission denied" errors
- On Linux: `sudo usermod -aG docker $USER` and logout/login

### Git permission errors
- Set git user: `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`

## Next Steps

Once all prerequisites are installed:

```bash
git clone https://github.com/AshraHossain/aerosense-testforge.git
cd aerosense-testforge
make setup
```

This will:
1. Create .env file
2. Install Python dependencies
3. Start Docker services
4. Run database migrations
5. Run tests to verify setup

Then you're ready to develop!
