# AgentCore Complete Example

Complete demonstration of Amazon Bedrock AgentCore components including Runtime, Gateway, Memory, and Observability in a customer support use case.

## 🚀 Quick Start

### 1. Deploy Everything
```bash
python deploy.py
```

### 2. Validate Solution
```bash
python validate.py
```

### 3. Test with Queries
```bash
python run_queries_example.py
```

### 4. Clean Up
```bash
python cleanup.py
```

## 📁 Project Structure

```
agentcore-complete-example/
├── deploy.py              # Complete deployment script
├── cleanup.py             # Complete cleanup script  
├── validate.py            # Solution validation script
├── run_queries_example.py # Query testing script
├── test_complete.py       # Working example test
├── agents/
│   ├── strands_agents.py # Core agent implementation
│   └── __init__.py
├── infrastructure/
│   ├── cloudformation/
│   │   └── customer-support.yaml
│   ├── lambda-functions/
│   │   └── streamable_http_sigv4.py
│   └── openapi-specs/
│       └── nasa_mars_insights.json
├── tools/
│   ├── web_search.py
│   └── __init__.py
├── utils/
│   ├── aws_helpers.py
│   ├── gateway_helpers.py
│   ├── memory_helpers.py
│   └── __init__.py
└── requirements.txt
```

## 🧪 Test Scenarios

### Gateway Integration Tests
- **Warranty Check**: "I have a Gaming Console Pro device, warranty serial number is MNO33333333"
- **Mars Weather**: "What is the weather in northern part of mars?"
- **Account Info**: "Hi, can you check my account information?"
- **Device Issues**: "My iPhone gets hot when charging, help!"

### Memory Feature Tests
- **Context Setting**: "My name is Alex and I'm interested in learning about AI"
- **Context Retrieval**: "Can you search for the latest AI trends in 2025?"
- **Memory Recall**: "What was my name again?"
- **Context Aggregation**: "Can you summarize what we've discussed?"

## 🏗️ Architecture

The solution demonstrates:

- **🚀 Runtime**: Serverless agent deployment with containerized execution
- **🌐 Gateway**: Lambda functions + NASA OpenAPI integration via MCP protocol
- **🧠 Memory**: Short-term conversation memory with context retention
- **📊 Observability**: CloudWatch logs, X-Ray tracing, GenAI dashboard

## 📋 Components Deployed

### AWS Resources
- CloudFormation stack with Lambda functions and DynamoDB tables
- S3 bucket for OpenAPI specifications
- IAM roles for AgentCore components
- ECR repository for containerized agent

### AgentCore Components
- **Gateway**: MCP server with Lambda and OpenAPI targets
- **Runtime**: Serverless agent hosting environment
- **Identity**: API key credential management
- **Observability**: Automatic monitoring and tracing

## 🔧 Configuration

The deployment uses:
- **Region**: us-east-1 (configurable)
- **Model**: Anthropic Claude 3.7 Sonnet
- **Auth**: AWS IAM with SigV4 for gateway access
- **Memory**: Short-term conversational memory
- **Tools**: Customer support + NASA Mars weather API

## 📊 Validation

The `validate.py` script tests:

1. **Runtime Invocation**: Basic agent functionality
2. **Gateway Integration**: Lambda and OpenAPI target usage
3. **Memory Features**: Context retention and recall
4. **Observability**: CloudWatch logs and X-Ray traces

## 🧹 Cleanup

The `cleanup.py` script removes:
- AgentCore Runtime and ECR repositories
- Gateway, targets, and credential providers
- CloudFormation stack and all AWS resources
- S3 bucket and local deployment files

## 🚨 Important Notes

- Ensure AWS credentials are configured before deployment
- The solution may incur AWS charges for compute and storage
- NASA API key is included for demo purposes only
- All resources are created in us-east-1 region by default

## 📖 Usage Examples

### Deploy and Test
```bash
# Deploy everything
python deploy.py

# Run validation
python validate.py

# Test specific queries
python run_queries_example.py

# Clean up when done
python cleanup.py
```

### Working Example Only
```bash
# Test without full deployment
python test_complete.py
```

This provides a complete, production-ready example of AgentCore integration with all components working together in a realistic customer support scenario.
