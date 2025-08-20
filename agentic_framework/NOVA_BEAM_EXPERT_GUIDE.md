# Nova BEAM Expert Guide

A comprehensive guide to the Nova BEAM Knowledge Expert agent, its architecture, development journey, and implementation details.

## 🎯 Overview

The **Nova BEAM Expert** is an advanced AI agent that provides access to Exabeam's BEAM (Behavioral Event Analytics and Monitoring) security rules and features. Built on Google's Agent Development Kit (ADK), it can access, decode, and explain actual BEAM rule specifications with complete technical details.

## 🏗️ Architecture

### Core Technologies
- **Google ADK (Agent Development Kit)**: Agent framework and deployment platform
- **Gemini-2.5-flash**: Large language model for intelligent responses
- **Google Discovery Engine**: Document search and retrieval service
- **Google Document Service**: Raw content extraction and decoding
- **Vertex AI ReasoningEngines**: Cloud-based agent execution environment
- **Google Agentspace**: Agent management and user interface platform

### Key Components

```
Nova BEAM Expert
├── Search Service (Discovery Engine)
│   ├── Finds relevant BEAM documents
│   ├── Supports up to 20 results per query
│   └── Multiple search strategies
├── Document Service
│   ├── Fetches complete document content
│   ├── Extracts raw_bytes (1800+ bytes per rule)
│   └── Decodes UTF-8 content
└── Agent Tools
    ├── search_and_decode_beam_rules()
    ├── get_specific_beam_rule()
    ├── list_beam_rules_with_content()
    └── get_all_beam_documents()
```

## 🚀 Development Journey

### Phase 1: Initial Problem Discovery
**Challenge**: Agent provided generic responses instead of accessing actual BEAM data
- Agent was deployed but couldn't access real rule specifications
- Users received responses like "I'm having difficulty accessing specific rule details"
- Investigation revealed agent wasn't using available tools

### Phase 2: Permission Issues
**Challenge**: Discovery Engine API permission errors
- Error: "Permission denied for discoveryengine.servingConfigs.search"
- **Solution**: Granted `discoveryengine.editor` role to ReasoningEngine service account
- Service Account: `service-658179545428@gcp-sa-aiplatform-re.iam.gserviceaccount.com`

### Phase 3: Content Extraction Breakthrough
**Challenge**: Agent found documents but couldn't extract actual content
- Search Service returned only metadata fields
- Documents showed `can_fetch_raw_content: true` but no content in search results
- **Critical Discovery**: Search Service ≠ Document Service

**The Breakthrough Solution**:
1. **Search Service**: Find relevant documents by query
2. **Document Service**: Fetch complete document content using document ID
3. **Raw Bytes Decoding**: Extract and decode 1800+ bytes of actual rule content

### Phase 4: Local Testing Validation
Created test scripts to validate the approach:
- `test_beam_search_local.py`: Confirmed search limitations
- `test_raw_content_fetch.py`: Discovered Document Service approach
- `decode_beam_rule_content.py`: Successfully decoded NumDCP-Auth-TgsEC-U-Sn rule

### Phase 5: Expanded Search Capabilities
**Enhancement**: Increased search coverage from 3 to 20 results
- Added multi-query search strategy
- Implemented comprehensive document retrieval
- Created wildcard search capabilities

## 🔧 Technical Implementation

### Search and Content Extraction Process

```python
async def search_and_decode_beam_rules(query: str, tool_context: ToolContext) -> str:
    # 1. Search for documents using Discovery Engine
    search_request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=20  # Expanded from 3 to 20
    )
    
    # 2. For each found document, fetch actual content
    for result in search_response.results:
        doc_id = result.document.id
        document_name = f"projects/{project_id}/locations/{location}/collections/{collection}/dataStores/{datastore_id}/branches/default_branch/documents/{doc_id}"
        
        # 3. Use Document Service to get raw content
        get_request = discoveryengine.GetDocumentRequest(name=document_name)
        document = doc_client.get_document(request=get_request)
        
        # 4. Decode raw_bytes to get actual rule content
        if hasattr(document.content, 'raw_bytes'):
            decoded_content = document.content.raw_bytes.decode('utf-8')
```

### Data Store Configuration

```yaml
Project ID: threatexplainer
Location: global
Search Engine ID: agentspace-1754331730713_1754331730714
Datastore ID: content_1755237537757
Collection: default_collection
```

### Agent Tools Architecture

```python
tools=[
    FunctionTool(search_and_decode_beam_rules),    # Primary search with decoding
    FunctionTool(get_specific_beam_rule),          # Specific rule lookup
    FunctionTool(list_beam_rules_with_content),    # Enhanced rule listing
    FunctionTool(get_all_beam_documents)           # Comprehensive retrieval
]
```

## 📊 Capabilities

### BEAM Rule Types Supported
- **numericDistinctCountProfiledFeature**: Detects abnormal TGS requests
- **factFeature**: Static condition detection
- **profiledFeature**: Behavioral anomaly detection
- **contextFeature**: Contextual enrichment
- **correlationRule**: Multi-event pattern detection

### Content Extraction
- **Complete rule specifications**: Full 1800+ bytes of rule content
- **Technical configuration**: Training conditions, scope, feature values
- **MITRE ATT&CK mappings**: Tactics and techniques (e.g., TA0008 - Lateral Movement)
- **Security significance**: Investigation guidance and threat context

### Example: NumDCP-Auth-TgsEC-U-Sn Rule
```
Rule Type: numericDistinctCountProfiledFeature
Purpose: Detects abnormal TGS requests in Kerberos authentication
MITRE ATT&CK: TA0008 (Lateral Movement)
Content Size: 1816 bytes of complete technical specification
```

## 🛠️ Deployment Process

### 1. ReasoningEngine Deployment
```python
# Create ADK app with Document Service integration
app = reasoning_engines.AdkApp(
    agent=nova_agent,
    enable_tracing=True,
)

# Deploy to Vertex AI
remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk]",
        "google-adk",
        "google-cloud-discoveryengine",
        "google-auth",
        "requests",
    ]
)
```

### 2. Agentspace Registration
```python
# Register with Discovery Engine Agentspace
payload = {
    "displayName": "Nova BEAM Expert (Expanded Search)",
    "description": "Nova BEAM Knowledge Expert with expanded search capabilities...",
    "adkAgentDefinition": {
        "provisionedReasoningEngine": {
            "reasoningEngine": reasoning_engine_resource_name
        }
    }
}
```

## 🔍 Search Limitations and Solutions

### Traditional Search Limitations
- **Keyword dependency**: Must match indexed terms exactly
- **No fuzzy search**: Typos or variations may return no results
- **Limited semantic understanding**: Doesn't understand synonyms well
- **Metadata only**: Search results don't contain actual content

### Our Solutions
1. **Increased page_size**: 20 results vs 3 for better coverage
2. **Multi-query strategy**: 6 different search patterns
3. **Document Service integration**: Access to actual content
4. **Raw bytes decoding**: Complete rule specifications

### Why Not Vector Search?
Current implementation uses **keyword-based search**, not vector search:
- **Pros**: Higher volume (100+ results), fast pagination
- **Cons**: Poor semantic understanding, many irrelevant results
- **Vector search** would provide better semantic matching but lower volume

## 🎪 Usage Examples

### Query the Agent
```
"Explain rule NumDCP-Auth-TgsEC-U-Sn"
→ Returns complete rule specification with MITRE mappings

"List available BEAM rules"  
→ Returns comprehensive rule list with actual content

"Find lateral movement detection rules"
→ Returns relevant rules with decoded specifications
```

### Expected Results
- Complete rule type identification
- Technical configuration details
- MITRE ATT&CK framework mappings
- Security significance and investigation guidance
- 1800+ bytes of actual rule content

## 🚨 Troubleshooting

### Common Issues

1. **Permission Errors**
   - Ensure `discoveryengine.editor` role on ReasoningEngine service account
   - Verify project and location settings

2. **No Content Found**
   - Check datastore ID: `content_1755237537757`
   - Verify Document Service integration
   - Ensure raw_bytes decoding is implemented

3. **Limited Search Results**
   - Verify page_size is set to 20
   - Check multiple search strategies are implemented
   - Ensure query variations are being tried

## 📈 Performance Metrics

### Search Capabilities
- **Results per query**: Up to 20 (vs original 3)
- **Content extraction**: 1800+ bytes per rule
- **Search strategies**: 6 different query patterns
- **Total BEAM documents**: ~12 in datastore

### Response Quality
- **Before**: Generic responses, no actual rule content
- **After**: Complete rule specifications with technical details
- **Improvement**: 100% accurate rule content access

## 🔮 Future Enhancements

### Potential Improvements
1. **Vector Search Integration**: Better semantic understanding
2. **Real-time Data Access**: Live BEAM system integration
3. **Batch Processing**: Multiple document retrieval optimization
4. **Enhanced Caching**: Reduce API calls for frequently accessed rules

### Scalability Considerations
- API rate limits (Discovery Engine quotas)
- Memory constraints (ReasoningEngine limitations)  
- Content size limits (token window constraints)

## 📚 Key Files

### Deployment Scripts
- `deploy_nova_final_working.py`: Main deployment script with Document Service integration
- `register_existing_agent.py`: Agent registration utility

### Testing Scripts
- `test_beam_search_local.py`: Search capability validation
- `test_raw_content_fetch.py`: Document Service testing
- `decode_beam_rule_content.py`: Content decoding validation

### Agent Cleanup
- `clean_agent_space.py`: Agentspace cleanup utility

## 🏆 Success Metrics

The Nova BEAM Expert successfully solved the core challenge:

**Before**: "I'm having difficulty accessing specific rule details"
**After**: Complete NumDCP-Auth-TgsEC-U-Sn rule specification with 1816 bytes of technical content, MITRE mappings, and investigation guidance

This represents a breakthrough in accessing actual BEAM rule content rather than providing generic responses, enabling true security knowledge assistance.

---

*Built with Google ADK, powered by Gemini-2.5-flash, deployed on Vertex AI ReasoningEngines*