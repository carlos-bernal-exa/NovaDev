# Standalone Exabeam MCP Server

A containerized MCP (Model Context Protocol) server for Exabeam case search operations with JWT authentication and Server-Sent Events (SSE) support.

## Features

- **JWT Authentication**: Secure access using JWT tokens provided by users
- **Server-Sent Events (SSE)**: Real-time streaming for AI agent connections
- **Containerized Deployment**: Docker container with environment-based secrets
- **Exabeam Integration**: Search cases via threat-center API
- **MCP Protocol**: Standard MCP server implementation
- **AI Agent Compatible**: Can connect to any AI agent supporting MCP/SSE

## Quick Start

1. **Build and Run Container**:
```bash
docker build -t exabeam-mcp-server .
docker run -p 8080:8080 \
  -e JWT_SECRET="your-jwt-secret-key" \
  -e EXABEAM_CLIENT_ID="your-client-id" \
  -e EXABEAM_CLIENT_SECRET="your-client-secret" \
  exabeam-mcp-server
```

2. **Connect AI Agent**:
```bash
# SSE endpoint for real-time events
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8080/events

# MCP endpoint for case search
curl -X POST http://localhost:8080/mcp/search-cases \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"limit": 10, "startTime": "2024-05-01T00:00:00Z"}'
```

## Architecture

```
┌─────────────────┐    JWT Auth    ┌──────────────────┐
│   AI Agent      │ ──────────────► │  MCP Server      │
│                 │                 │  (Container)     │
└─────────────────┘                 └──────────────────┘
                                             │
                                             │ Bearer Token
                                             ▼
                                    ┌──────────────────┐
                                    │  Exabeam API     │
                                    │  threat-center   │
                                    └──────────────────┘
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `JWT_SECRET` | Secret key for JWT token validation | Yes |
| `EXABEAM_CLIENT_ID` | Exabeam API client ID | Yes |
| `EXABEAM_CLIENT_SECRET` | Exabeam API client secret | Yes |
| `EXABEAM_BASE_URL` | Exabeam API base URL | No (default: https://api.us-west.exabeam.cloud) |
| `PORT` | Server port | No (default: 8080) |

## API Endpoints

### SSE Events
- `GET /events` - Server-sent events stream for real-time updates
- Requires JWT authentication via `Authorization: Bearer <token>`

### MCP Operations
- `POST /mcp/search-cases` - Search Exabeam cases
- `GET /mcp/tools` - List available MCP tools
- `GET /health` - Health check endpoint

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python src/main.py

# Run tests
pytest tests/
```
