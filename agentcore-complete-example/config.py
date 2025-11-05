#!/usr/bin/env python3
"""
Configuration Settings for AgentCore Complete Example

This module centralizes all configurable values for the AgentCore deployment,
making it easy to customize the deployment for different environments.
"""

import os

class Config:
    """Configuration class for AgentCore deployment"""
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # CloudFormation Configuration
    STACK_NAME = os.getenv('STACK_NAME', 'agentcore-customer-support')
    CLOUDFORMATION_TEMPLATE = "infrastructure/cloudformation/customer-support.yaml"
    
    # S3 Configuration
    OPENAPI_SPEC_PATH = "infrastructure/openapi-specs/nasa_mars_insights.json"
    OPENAPI_SPEC_KEY = "nasa_mars_insights.json"
    
    # Gateway Configuration
    GATEWAY_NAME_PREFIX = os.getenv('GATEWAY_NAME_PREFIX', 'customer-support-gateway')
    GATEWAY_ROLE_PREFIX = os.getenv('GATEWAY_ROLE_PREFIX', 'agentcore-gateway-role')
    GATEWAY_DESCRIPTION = "Customer support gateway with Lambda and OpenAPI targets"
    
    # Runtime Configuration
    AGENT_NAME = os.getenv('AGENT_NAME', 'customer_support_agent')
    AGENT_ENTRYPOINT = "agents/runtime_agent.py"
    REQUIREMENTS_FILE = "requirements.txt"
    
    # API Keys
    NASA_API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')
    
    # Target Names
    LAMBDA_TARGET_NAME = "CustomerSupportLambda"
    OPENAPI_TARGET_NAME = "NASAMarsInsights"
    
    # Deployment Settings
    DEPLOYMENT_INFO_FILE = "deployment_info.json"
    
    @classmethod
    def get_gateway_name(cls):
        """Generate unique gateway name"""
        import uuid
        return f"{cls.GATEWAY_NAME_PREFIX}-{str(uuid.uuid4())[:8]}"
    
    @classmethod
    def get_gateway_role_name(cls):
        """Generate unique gateway role name"""
        import uuid
        return f"{cls.GATEWAY_ROLE_PREFIX}-{str(uuid.uuid4())[:8]}"
    
    @classmethod
    def get_s3_bucket_name(cls):
        """Generate unique S3 bucket name"""
        import uuid
        return f"agentcore-gateway-{str(uuid.uuid4())}"
    
    @classmethod
    def get_credential_provider_name(cls):
        """Generate unique credential provider name"""
        import uuid
        return f"nasa-api-credentials-{str(uuid.uuid4())[:8]}"