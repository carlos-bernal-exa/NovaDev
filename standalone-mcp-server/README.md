# Standalone Exabeam MCP Server

A containerized MCP (Model Context Protocol) server for Exabeam case search operations with JWT authentication and Server-Sent Events (SSE) support. This server can be deployed independently and connected to any AI agent.

## 🚀 Features

- **JWT Authentication**: Secure access using JWT tokens (HS256/RS256) with user-provided secrets
- **Server-Sent Events (SSE)**: Real-time streaming for AI agent connections
- **HashiCorp Vault Integration**: Secure secret storage and retrieval
- **Containerized Deployment**: Docker container with health checks and security best practices
- **Exabeam Integration**: Search cases via threat-center API with automatic token management
- **MCP Protocol**: Standard MCP server implementation
- **AI Agent Compatible**: Can connect to any AI agent supporting HTTP/SSE
- **Production Ready**: Nginx reverse proxy, CORS support, comprehensive logging

## 📋 Prerequisites

Before you begin, ensure you have:

- **Docker** and **Docker Compose** installed
- **Exabeam API credentials** (client ID and secret)
- **JWT secret key** for token validation
- (Optional) **HashiCorp Vault** for secure secret management

## 🛠️ Quick Start Guide

### Step 1: Clone and Setup

```bash
# Navigate to the standalone MCP server directory
cd standalone-mcp-server

# Copy environment template
cp .env.example .env
```

### Step 2: Generate JWT Secret

**IMPORTANT**: Generate your JWT secret FIRST before configuring the .env file:

#### Option A: Generate Random Secret (Recommended)
```bash
# Generate a cryptographically secure random secret
JWT_SECRET=$(openssl rand -base64 32)
echo "Generated JWT Secret: $JWT_SECRET"

# Alternative methods if openssl is not available:
# Using Python
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Using Node.js
JWT_SECRET=$(node -e "console.log(require('crypto').randomBytes(32).toString('base64'))")

# Using /dev/urandom (Linux/macOS)
JWT_SECRET=$(head -c 32 /dev/urandom | base64)
```

#### Option B: Create Your Own Secret
```bash
# Use any strong, unique string (minimum 32 characters recommended)
JWT_SECRET="my-super-secure-jwt-secret-key-$(date +%s)-$(whoami)"

# Or use a passphrase-based approach
JWT_SECRET="MyCompany-ExabeamMCP-$(date +%Y%m%d)-SecretKey"
```

#### Option C: Use Password Manager
```bash
# Generate using password managers:
# - 1Password: Generate 32+ character password
# - LastPass: Generate secure note with 32+ characters  
# - Bitwarden: Generate password with symbols, 32+ length
# Then set: JWT_SECRET="your-generated-password-here"
```

**Security Notes:**
- Minimum 32 characters recommended
- Include letters, numbers, and symbols
- Never reuse secrets across environments
- Store securely (consider using HashiCorp Vault - see Step 3)
- Keep different secrets for dev/staging/production

### Step 3: Configure Environment Variables

Edit the `.env` file with your credentials, **using the JWT secret from Step 2**:

```bash
# Required: JWT Authentication (use the secret from Step 2)
JWT_SECRET=your-super-secure-jwt-secret-key-here

# Required: Exabeam API Credentials
EXABEAM_CLIENT_ID=your-exabeam-client-id
EXABEAM_CLIENT_SECRET=your-exabeam-client-secret
EXABEAM_BASE_URL=https://api.us-west.exabeam.cloud

# Optional: Server Configuration
PORT=8080
LOG_LEVEL=INFO

# Optional: HashiCorp Vault Integration
VAULT_ENABLED=false
VAULT_URL=https://vault.example.com:8200
VAULT_TOKEN=your-vault-token
VAULT_SECRET_PATH=secret/exabeam-mcp
```

### Step 4: Generate JWT Tokens for Testing

**After** configuring your .env file, generate test JWT tokens:

```bash
# Generate a test JWT token (note: all 5 parameters are required)
python scripts/generate_token.py generate "your-super-secure-jwt-secret-key-here" "user123" "Test User" true 24

# Common mistake - missing display name (will show helpful error):
# python scripts/generate_token.py generate "your-super-secure-jwt-secret-key-here" "user123" true 24  # ❌ Wrong

# Correct format with your actual secret:
python scripts/generate_token.py generate "JHoM0t4t6ROLHqUN8t9Cvg7wws/PoHyMaeQuTJOMAgU=" "Carlito" "Carlito User" true 24

# Example output:
# Generated JWT Token:
# Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 5: Deploy with Docker

**Option A: Docker Compose (Recommended)**
```bash
# Start the complete stack (MCP server + Nginx)
docker-compose up -d

# Check status
docker-compose ps
```

**Option B: Docker Run**
```bash
# Build the image
docker build -t exabeam-mcp-server .

# Run the container
docker run -d -p 8080:8080 \
  --env-file .env \
  --name exabeam-mcp-server \
  exabeam-mcp-server
```

### Step 6: Test the Deployment

```bash
# Test the comprehensive connection script
python scripts/test_connection.py http://localhost:8080 "your-super-secure-jwt-secret-key-here"

# Manual testing
curl http://localhost:8080/health
```

## 🏗️ Architecture

```
┌─────────────────┐    JWT Auth    ┌──────────────────┐    ┌─────────────────┐
│   AI Agent      │ ──────────────► │  Nginx Proxy     │───►│  MCP Server     │
│                 │                 │  (Port 80)       │    │  (Port 8080)    │
│  - Claude       │                 │                  │    │                 │
│  - ChatGPT      │    SSE Stream   │  - CORS          │    │  - JWT Auth     │
│  - Custom Agent │ ◄──────────────│  - Load Balance  │◄───│  - SSE Events   │
└─────────────────┘                 │  - SSL Term      │    │  - Case Search  │
                                    └──────────────────┘    └─────────────────┘
                                                                      │
                                    ┌─────────────────┐              │ Bearer Token
                                    │  HashiCorp      │              ▼
                                    │  Vault          │    ┌──────────────────┐
                                    │  (Optional)     │    │  Exabeam API     │
                                    └─────────────────┘    │  threat-center   │
                                                          └──────────────────┘
```

## 📝 Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET` | Secret key for JWT token validation | `your-super-secure-jwt-secret-key-here` |
| `EXABEAM_CLIENT_ID` | Exabeam API client ID | `5SDo7FpB1BNFfBzPX65MGh2eWn3W1TLqcR3so3AUZQ8GSz27` |
| `EXABEAM_CLIENT_SECRET` | Exabeam API client secret | `iuv91DLwKhFwGk1361aEIsuG5OGTbWnp1JvEtm5CP5uAvPGJxViaB6qKm5GYADYE` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `EXABEAM_BASE_URL` | Exabeam API base URL | `https://api.us-west.exabeam.cloud` | `https://api.eu-west.exabeam.cloud` |
| `PORT` | Server port | `8080` | `9000` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | `RS256` |

### HashiCorp Vault Integration (Optional)

| Variable | Description | Example |
|----------|-------------|---------|
| `VAULT_ENABLED` | Enable Vault integration | `true` |
| `VAULT_URL` | Vault server URL | `https://vault.example.com:8200` |
| `VAULT_TOKEN` | Vault authentication token | `hvs.CAESIJ...` |
| `VAULT_SECRET_PATH` | Path to secrets in Vault | `secret/exabeam-mcp` |
| `VAULT_MOUNT_POINT` | Vault mount point | `secret` |

## 🔌 AI Agent Integration

### Connecting Any AI Agent

The MCP server provides standard HTTP endpoints that any AI agent can connect to:

#### 1. Authentication Setup
```python
# Example: Python AI Agent
import requests
import json

# Your JWT token (generated using scripts/generate_token.py)
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {"Authorization": f"Bearer {jwt_token}"}

# Test connection
response = requests.get("http://localhost:8080/mcp/tools", headers=headers)
print(response.json())
```

#### 2. Server-Sent Events (SSE) Connection
```javascript
// Example: JavaScript AI Agent
const eventSource = new EventSource('http://localhost:8080/events', {
  headers: {
    'Authorization': 'Bearer ' + jwt_token
  }
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

eventSource.addEventListener('connected', function(event) {
  console.log('Connected to MCP server');
});
```

#### 3. Case Search Operations
```bash
# Search Exabeam cases
curl -X POST http://localhost:8080/mcp/search-cases \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 100,
    "start_time": "2024-05-01T00:00:00Z",
    "end_time": "2024-06-01T00:00:00Z",
    "fields": ["*"],
    "filter_query": "product: (\"Correlation Rule\", \"NG Analytics\")"
  }'
```

## 🔐 HashiCorp Vault Integration

For production deployments, use HashiCorp Vault to securely store secrets:

### Setup Vault Integration

1. **Configure Vault Secrets**:
```bash
# Store secrets in Vault
vault kv put secret/exabeam-mcp \
  jwt_secret="your-super-secure-jwt-secret-key-here" \
  exabeam_client_id="your-exabeam-client-id" \
  exabeam_client_secret="your-exabeam-client-secret"
```

2. **Enable Vault in Environment**:
```bash
# .env file
VAULT_ENABLED=true
VAULT_URL=https://vault.example.com:8200
VAULT_TOKEN=hvs.CAESIJ...
VAULT_SECRET_PATH=secret/exabeam-mcp
```

3. **Deploy with Vault**:
```bash
# The server will automatically fetch secrets from Vault on startup
docker-compose up -d
```

### Vault Authentication Methods

The server supports multiple Vault authentication methods:

- **Token Authentication** (default): Use `VAULT_TOKEN`
- **AppRole Authentication**: Set `VAULT_ROLE_ID` and `VAULT_SECRET_ID`
- **Kubernetes Authentication**: Set `VAULT_K8S_ROLE`

## 📊 API Endpoints Reference

### Health & Status
- `GET /health` - Health check endpoint (no auth required)
- `GET /mcp/token-status` - Check Exabeam token status (JWT required)

### Authentication
- All endpoints except `/health` require JWT authentication
- Include header: `Authorization: Bearer <your-jwt-token>`

### MCP Operations
- `GET /mcp/tools` - List available MCP tools
- `POST /mcp/search-cases` - Search Exabeam cases

### Real-time Events
- `GET /events` - Server-sent events stream for real-time updates

### Example Responses

**GET /mcp/tools**:
```json
{
  "tools": [
    {
      "name": "search_cases",
      "description": "Search Exabeam security cases",
      "parameters": {
        "limit": "Maximum number of cases to return",
        "start_time": "Start time in ISO format",
        "end_time": "End time in ISO format",
        "fields": "List of fields to return",
        "filter_query": "Filter query string"
      }
    }
  ],
  "user": "CARLITOTESTMCP",
  "timestamp": "2025-08-14T12:42:53.143076"
}
```

**POST /mcp/search-cases**:
```json
{
  "data": {
    "cases": [
      {
        "caseId": "12345",
        "title": "Suspicious Login Activity",
        "severity": "High",
        "status": "Open",
        "createdTime": "2024-05-15T10:30:00Z"
      }
    ],
    "totalCount": 1
  },
  "timestamp": "2025-08-14T12:42:53.143076"
}
```

## 🚀 Production Deployment

### Docker Compose with Nginx (Recommended)

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - exabeam-mcp-server

  exabeam-mcp-server:
    build: .
    environment:
      - VAULT_ENABLED=true
      - VAULT_URL=${VAULT_URL}
      - VAULT_TOKEN=${VAULT_TOKEN}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: exabeam-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: exabeam-mcp-server
  template:
    metadata:
      labels:
        app: exabeam-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: exabeam-mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: VAULT_ENABLED
          value: "true"
        - name: VAULT_K8S_ROLE
          value: "exabeam-mcp"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Security Considerations

1. **JWT Secret Management**:
   - Use strong, randomly generated secrets (minimum 256 bits)
   - Rotate secrets regularly
   - Store in HashiCorp Vault or Kubernetes secrets

2. **Network Security**:
   - Use HTTPS in production (configure SSL in Nginx)
   - Implement rate limiting
   - Use firewall rules to restrict access

3. **Container Security**:
   - Run as non-root user (already configured)
   - Use minimal base images
   - Scan for vulnerabilities regularly

## 🧪 Development & Testing

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run locally
python src/main.py

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Testing with Different AI Agents

```bash
# Test with comprehensive script
python scripts/test_connection.py http://localhost:8080 "your-jwt-secret"

# Test individual endpoints
curl http://localhost:8080/health
curl -H "Authorization: Bearer ${JWT_TOKEN}" http://localhost:8080/mcp/tools

# Test SSE connection
curl -H "Authorization: Bearer ${JWT_TOKEN}" \
     -H "Accept: text/event-stream" \
     http://localhost:8080/events
```

### Debugging

```bash
# View container logs
docker-compose logs -f exabeam-mcp-server

# Debug mode
LOG_LEVEL=DEBUG docker-compose up

# Test Vault connection
python scripts/test_vault.py
```

## 🔧 Troubleshooting

### Common Issues

1. **JWT Token Generation Errors**:
   - **Missing display name parameter**: The script requires 5 parameters: `<secret> <user_id> <display_name> <admin> <hours>`
     ```bash
     # ❌ Wrong (missing display name):
     python3 scripts/generate_token.py generate "secret" "user" true 24
     
     # ✅ Correct:
     python3 scripts/generate_token.py generate "secret" "user" "User Name" true 24
     ```
   - **Special characters in JWT secret**: Always quote secrets containing special characters like `=`, `/`, `+`
     ```bash
     python3 scripts/generate_token.py generate "JHoM0t4t6ROLHqUN8t9Cvg7wws/PoHyMaeQuTJOMAgU=" "user" "User Name" true 24
     ```

2. **JWT Authentication Fails**:
   - Verify JWT_SECRET matches token generation
   - Check token expiration
   - Ensure proper Authorization header format

3. **Exabeam API Connection Issues**:
   - Verify EXABEAM_CLIENT_ID and EXABEAM_CLIENT_SECRET
   - Check network connectivity to Exabeam API
   - Review Exabeam token expiration

4. **Container Won't Start**:
   - Check environment variables are set
   - Verify Docker has sufficient resources
   - Review container logs for specific errors

5. **SSE Connection Drops**:
   - Check network stability
   - Verify JWT token hasn't expired
   - Review Nginx proxy configuration

### Support

For issues and questions:
- Check the logs: `docker-compose logs -f`
- Run the test suite: `python scripts/test_connection.py`
- Review the troubleshooting section above
- Open an issue in the repository
