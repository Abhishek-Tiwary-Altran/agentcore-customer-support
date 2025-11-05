#!/usr/bin/env python3
"""
AgentCore Runtime Agent - Customer Support

This module contains the runtime agent implementation for AgentCore deployment.
It integrates with AgentCore Gateway for tool access and provides the main
entrypoint for the customer support agent.
"""

import os
import sys
import boto3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import SigV4 client - handle import gracefully
try:
    from infrastructure.lambda_functions.streamable_http_sigv4 import streamablehttp_client_with_sigv4
except ImportError:
    try:
        from streamable_http_sigv4 import streamablehttp_client_with_sigv4
    except ImportError:
        def streamablehttp_client_with_sigv4(*args, **kwargs):
            raise ImportError("SigV4 client not available")

# Initialize AgentCore app
app = BedrockAgentCoreApp()

def create_mcp_client():
    """Create MCP client with SigV4 authentication for AgentCore Gateway."""
    gateway_url = os.getenv('GATEWAY_URL')
    if not gateway_url:
        raise ValueError("GATEWAY_URL environment variable not set")
    
    session = boto3.Session()
    credentials = session.get_credentials()
    
    return MCPClient(
        lambda: streamablehttp_client_with_sigv4(
            url=gateway_url,
            credentials=credentials,
            service="bedrock-agentcore",
            region=os.getenv('GATEWAY_REGION', 'us-east-1')
        )
    )

def get_tools():
    """Get available tools from AgentCore Gateway."""
    tools = []
    try:
        mcp_client = create_mcp_client()
        mcp_client.start()
        tool_list = mcp_client.list_tools_sync()
        tools.extend(tool_list)
    except Exception as e:
        print(f"Warning: Could not load gateway tools: {e}")
    return tools

def create_customer_support_agent():
    """Create the customer support agent with AgentCore integration."""
    
    # Get tools from gateway
    tools = get_tools()
    
    # Create agent with comprehensive system prompt
    system_prompt = """You are an intelligent customer support agent for a technology company.

Your capabilities:
✅ Access customer profiles and order history
✅ Check warranty status for devices  
✅ Search knowledge base for solutions
✅ Research current information via web search

Guidelines:
- Always be professional, helpful, and empathetic
- Use customer tools to get accurate information
- Provide step-by-step troubleshooting when possible
- Reference previous orders when relevant
- Escalate complex issues to human specialists when needed

You have access to customer data, warranty information, and can search for current solutions."""

    model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    agent = Agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    return agent

# Create the agent instance
agent = create_customer_support_agent()

@app.entrypoint
def customer_support_agent(payload):
    """Main entrypoint for AgentCore Runtime."""
    user_input = payload.get("prompt", "")
    
    if not user_input:
        return "Hello! I'm your customer support agent. How can I help you today?"
    
    try:
        response = agent(user_input)
        return response.message['content'][0]['text']
    except Exception as e:
        return f"I apologize, but I encountered an error processing your request: {str(e)}"

if __name__ == "__main__":
    app.run()