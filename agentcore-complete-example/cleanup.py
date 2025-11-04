#!/usr/bin/env python3
"""
Complete AgentCore Cleanup Script

Cleans up all deployed AWS resources and AgentCore components:
- AgentCore Runtime and ECR repositories
- AgentCore Gateway and targets
- CloudFormation stack (Lambda, DynamoDB, IAM roles)
- S3 bucket and objects
- API key credential providers
"""

import sys
import os
import json
import boto3
from pathlib import Path

sys.path.append('.')

def load_deployment_info():
    """Load deployment information from file"""
    try:
        with open("deployment_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ deployment_info.json not found. Run deploy.py first.")
        return None
    except Exception as e:
        print(f"❌ Error loading deployment info: {e}")
        return None

def cleanup_runtime(deployment_info):
    """Clean up AgentCore Runtime and ECR"""
    print("🚀 Cleaning up AgentCore Runtime...")
    
    try:
        from bedrock_agentcore_starter_toolkit import Runtime
        from bedrock_agentcore_starter_toolkit.operations.runtime import destroy_bedrock_agentcore
        
        # Delete runtime using toolkit
        destroy_bedrock_agentcore(
            config_path=Path(".bedrock_agentcore.yaml"),
            agent_name="customer-support-agent",
            delete_ecr_repo=True
        )
        
        print("✅ Runtime and ECR cleaned up")
        
    except Exception as e:
        print(f"⚠️ Runtime cleanup warning: {e}")
        
        # Fallback: try direct API cleanup
        try:
            agentcore_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
            ecr_client = boto3.client('ecr', region_name='us-east-1')
            
            # Try to delete runtime directly
            if 'runtime' in deployment_info and 'agent_arn' in deployment_info['runtime']:
                agent_id = deployment_info['runtime']['agent_arn'].split('/')[-1]
                try:
                    agentcore_client.delete_agent_runtime(agentRuntimeId=agent_id)
                    print("✅ Runtime deleted via API")
                except:
                    pass
            
            # Try to delete ECR repository
            try:
                ecr_client.delete_repository(
                    repositoryName="bedrock-agentcore-customer-support-agent",
                    force=True
                )
                print("✅ ECR repository deleted")
            except:
                pass
                
        except Exception as fallback_error:
            print(f"⚠️ Fallback runtime cleanup failed: {fallback_error}")

def cleanup_gateway(deployment_info):
    """Clean up AgentCore Gateway and targets"""
    print("🌐 Cleaning up AgentCore Gateway...")
    
    try:
        agentcore_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        if 'gateway' in deployment_info:
            gateway_id = deployment_info['gateway']['gateway_id']
            
            # List and delete targets first
            try:
                targets = agentcore_client.list_gateway_targets(gatewayIdentifier=gateway_id)
                for target in targets.get('items', []):
                    agentcore_client.delete_gateway_target(
                        gatewayIdentifier=gateway_id,
                        targetIdentifier=target['targetId']
                    )
                    print(f"✅ Deleted gateway target: {target['name']}")
            except Exception as e:
                print(f"⚠️ Target cleanup warning: {e}")
            
            # Delete gateway
            agentcore_client.delete_gateway(gatewayIdentifier=gateway_id)
            print("✅ Gateway deleted")
        
        # Clean up API key credential provider
        try:
            agentcore_client.delete_api_key_credential_provider(name="NasaAPIKey")
            print("✅ API key credential provider deleted")
        except Exception as e:
            print(f"⚠️ Credential provider cleanup warning: {e}")
            
    except Exception as e:
        print(f"⚠️ Gateway cleanup warning: {e}")

def cleanup_s3(deployment_info):
    """Clean up S3 bucket and objects"""
    print("📦 Cleaning up S3 bucket...")
    
    try:
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        if 's3' in deployment_info:
            bucket_name = deployment_info['s3']['bucket_name']
            
            # Delete all objects
            try:
                objects = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in objects:
                    for obj in objects['Contents']:
                        s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                        print(f"✅ Deleted object: {obj['Key']}")
            except Exception as e:
                print(f"⚠️ Object deletion warning: {e}")
            
            # Delete bucket
            s3_client.delete_bucket(Bucket=bucket_name)
            print(f"✅ S3 bucket deleted: {bucket_name}")
            
    except Exception as e:
        print(f"⚠️ S3 cleanup warning: {e}")

def cleanup_cloudformation(deployment_info):
    """Clean up CloudFormation stack"""
    print("📋 Cleaning up CloudFormation stack...")
    
    try:
        cf_client = boto3.client('cloudformation', region_name='us-east-1')
        
        stack_name = "agentcore-customer-support"
        
        # Delete stack
        cf_client.delete_stack(StackName=stack_name)
        
        # Wait for deletion
        waiter = cf_client.get_waiter('stack_delete_complete')
        print("⏳ Waiting for stack deletion...")
        waiter.wait(StackName=stack_name, WaiterConfig={'Delay': 30, 'MaxAttempts': 20})
        
        print("✅ CloudFormation stack deleted")
        
    except Exception as e:
        print(f"⚠️ CloudFormation cleanup warning: {e}")

def cleanup_local_files():
    """Clean up local deployment files"""
    print("🧹 Cleaning up local files...")
    
    files_to_remove = [
        "deployment_info.json",
        "runtime_agent.py",
        ".bedrock_agentcore.yaml",
        "Dockerfile",
        ".dockerignore"
    ]
    
    for file_path in files_to_remove:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
        except Exception as e:
            print(f"⚠️ Could not remove {file_path}: {e}")

def main():
    """Main cleanup function"""
    print("🧹 AgentCore Complete Cleanup")
    print("=" * 50)
    
    # Load deployment info
    deployment_info = load_deployment_info()
    if not deployment_info:
        return 1
    
    # Confirm cleanup
    print("This will delete ALL deployed resources:")
    if 'gateway' in deployment_info:
        print(f"  - Gateway: {deployment_info['gateway']['gateway_id']}")
    if 'runtime' in deployment_info:
        print(f"  - Runtime: {deployment_info['runtime']['agent_arn']}")
    if 's3' in deployment_info:
        print(f"  - S3 Bucket: {deployment_info['s3']['bucket_name']}")
    print("  - CloudFormation stack: agentcore-customer-support")
    
    confirm = input("\nAre you sure you want to proceed? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cleanup cancelled.")
        return 0
    
    try:
        # Step 1: Clean up Runtime (first, as it depends on other resources)
        cleanup_runtime(deployment_info)
        
        # Step 2: Clean up Gateway
        cleanup_gateway(deployment_info)
        
        # Step 3: Clean up S3
        cleanup_s3(deployment_info)
        
        # Step 4: Clean up CloudFormation (last, as other resources depend on it)
        cleanup_cloudformation(deployment_info)
        
        # Step 5: Clean up local files
        cleanup_local_files()
        
        print("\n🎉 Cleanup completed successfully!")
        print("All AgentCore resources have been removed.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        print("Some resources may need manual cleanup.")
        return 1

if __name__ == "__main__":
    exit(main())