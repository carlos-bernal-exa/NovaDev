# Agentic Security Framework

A multi-agent security framework built with Google ADK that uses a concierge agent to route security-related queries to specialized agents powered by Gemini-2.5-flash.

## Features

- **Concierge Agent**: Intelligent intent detection and routing to specialized agents
- **Specialized Security Agents**: 
  - ThreatAnalyst: Cybersecurity threats, malware, and security incidents
  - ComplianceExpert: Compliance, regulations, and security frameworks
  - IncidentResponder: Security incident response and forensics
  - SecurityArchitect: Security architecture and technical solutions
- **Gemini-2.5-flash Integration**: Powered by Google's latest language model via Vertex AI
- **Exabeam MCP Integration**: Automatic token management with TTL tracking and refresh
- **Robust Token Management**: Automatic refresh before expiration with 120-second skew

## Architecture

The framework implements the coordinator/dispatcher pattern from Google ADK:
1. User queries are received by the Concierge Agent
2. Concierge analyzes intent and routes to appropriate specialized agent
3. Specialized agents use Gemini-2.5-flash to generate responses
4. MCP client manages Exabeam API tokens automatically

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Configure environment variables in `.env`:
```bash
# Vertex AI Configuration
GOOGLE_APPLICATION_CREDENTIALS=./vertex_ai_credentials.json
GOOGLE_CLOUD_PROJECT=threatexplainer
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# Exabeam API Configuration
EXABEAM_API_BASE_URL=https://api.us-west.exabeam.cloud
EXABEAM_TOKEN_ENDPOINT=/auth/v1/token
EXABEAM_CLIENT_ID=your_client_id
EXABEAM_CLIENT_SECRET=your_client_secret
TOKEN_SKEW_SECONDS=120
```

3. Add your Vertex AI credentials file and update the path in `.env`:
```bash
GOOGLE_APPLICATION_CREDENTIALS=./path/to/your/vertex_ai_credentials.json
```

## Usage

### Running the Demo
```bash
poetry run python app/demo.py
```

### Using the Framework
```python
from app.framework import AgenticFramework

framework = AgenticFramework()
response = await framework.process_query(
    "I need help analyzing a suspicious email attachment", 
    session_id="my_session"
)
print(response)
```

## Testing

The framework includes comprehensive testing for:
- Intent detection and routing
- Gemini-2.5-flash integration via Vertex AI
- Exabeam token management and automatic refresh
- End-to-end query processing

Run tests with:
```bash
poetry run python app/demo.py
```

## Components

### AgenticFramework
Main orchestrator that initializes all components and handles query processing.

### ConciergeAgent
Routes user requests to appropriate specialized agents based on intent detection.

### SpecializedAgent
Base class for domain-specific agents that handle specialized security queries.

### ExabeamTokenManager
Manages Exabeam API tokens with automatic refresh and TTL tracking.

### ExabeamMCPClient
MCP client for connecting to Exabeam services (when MCP server is available).

## Security Features

- Automatic token refresh before expiration
- Secure credential management via environment variables
- Comprehensive logging for audit trails
- Intent-based routing for specialized security expertise

## Requirements

- Python 3.12+
- Poetry for dependency management
- Google Cloud Vertex AI access
- Exabeam API credentials
- google-adk package

## License

This project is part of the NovaDev repository.
