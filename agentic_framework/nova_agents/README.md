# Nova AI Framework

Nova is a specialized AI framework within Exabeam's agentic system, designed to help users understand BEAM Features, Correlation Rules, and create precise exclusions to reduce false positives.

## Architecture

Nova implements a **dual-agent routing system**:

### 🏨 **Routing Agent** (`agents/routing_agent.py`)
- Analyzes user intent to determine the appropriate knowledge base mode
- Routes queries based on whether user needs rule explanation or exclusion creation
- Powered by Gemini-2.5-flash for intelligent intent detection

### 🧠 **Knowledge Agent** (`agents/knowledge_agent.py`) 
- **Dual-mode operation** with specialized prompts:
  - **DETECTION_EXPLANATION_MODE**: Explains how BEAM Features and Correlation Rules work
  - **EXCLUSION_CREATION_MODE**: Helps create exclusions and reduce false positives
- Direct access to `content_1755237537757` data store via MCP tools
- Powered by Gemini-2.5-flash for technical analysis

## Features

### 🎯 **Detection Explanation Mode**
- Explains BEAM rule types: `factFeature`, `profiledFeature`, `contextFeature`, numeric variants
- Describes Correlation Rules (`rule_sequence`) with patterns and conditions  
- Maps detections to MITRE ATT&CK techniques
- Provides security context and threat relevance

### 🛠️ **Exclusion Creation Mode**
- Crafts precise BEAM exclusion expressions
- Uses Exabeam's Common Information Model (CIM)
- Leverages full BEAM function library (Boolean, String, Math, Time, Context, etc.)
- Balances false positive reduction with security signal preservation

### 🗄️ **Data Store Integration**
- Direct access to `content_1755237537757` vector store
- Search BEAM Features by rule type, activity type, or free text
- Query Correlation Rules by use case, MITRE techniques, or patterns
- Rule lookup by ID for detailed analysis

## Usage

### Running the Demo
```bash
cd nova_agents
python demo.py
```

### Using the Framework
```python
from nova_agents.nova_framework import NovaFramework

# Initialize Nova
framework = NovaFramework(datastore_id="content_1755237537757")

# Process queries (auto-routed to appropriate mode)
response = await framework.process_query(
    "How does the rundll32 ZxShell detection work?"
)

# Direct data store searches
beam_results = await framework.search_beam_features(
    query="process creation anomaly",
    rule_types=["factFeature", "profiledFeature"]
)

# Manual mode setting
framework.set_knowledge_agent_mode("EXCLUSION_CREATION_MODE")
```

## Components

### NovaFramework (`nova_framework.py`)
Main orchestrator that manages agent routing and data store integration.

### NovaRoutingAgent (`agents/routing_agent.py`)
Determines user intent and routes to appropriate knowledge base mode:
- Detection explanation queries → `DETECTION_EXPLANATION_MODE`
- Exclusion/tuning queries → `EXCLUSION_CREATION_MODE`

### NovaKnowledgeAgent (`agents/knowledge_agent.py`)
Dual-mode agent with specialized prompts for:
- **Rule Explanation**: Interprets BEAM Features and Correlation Rules
- **Exclusion Creation**: Generates BEAM expressions using function library

### NovaDataStoreClient (`data/datastore_client.py`)
Handles vector store queries for `content_1755237537757`:
- BEAM Feature searches with rule type filtering
- Correlation Rule searches with use case filtering
- Activity type-based rule discovery

## Supported Rule Types

### BEAM Features
- **factFeature**: Static condition detection
- **profiledFeature**: Behavioral anomaly detection
- **contextFeature**: Contextual enrichment
- **numeric count/distinct/sum profiledFeature**: Quantitative anomalies

### Correlation Rules
- **rule_sequence**: Multi-event pattern detection with conditional logic

## BEAM Expression Functions

### Boolean & Logical
`and()`, `or()`, `not()`, `in()`, `exists()`, `if()`, `returnIf()`

### String Functions  
`startsWith()`, `endsWith()`, `contains()`, `concat()`, `toLower()`, `trim()`, etc.

### Numeric & Math
`add()`, `subtract()`, `multiply()`, `max()`, `min()`, `floor()`, `ceil()`, etc.

### Time Functions
`timeofday()`, `timeofweek()`, `hour()`, etc.

### Context & Entity
`ContextListContains()`, `HasUserAttribute()`, `GetEntityAttribute()`, etc.

## Requirements

- Python 3.12+
- Google ADK with Gemini-2.5-flash
- Access to `content_1755237537757` data store
- Vertex AI credentials
- MCP integration for vector store queries

## Environment Setup

```bash
# Vertex AI Configuration
GOOGLE_APPLICATION_CREDENTIALS=./vertex_ai_credentials.json
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1

# Logging
LOG_LEVEL=INFO
```

Nova provides intelligent, context-aware assistance for understanding Exabeam's detection logic and creating precise exclusions that maintain security efficacy while reducing operational noise.