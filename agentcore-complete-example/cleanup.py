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
from config import Config

def load_deployment_info():
    """Load deployment information from file"""
    try:
        with open(Config.DEPLOYMENT_INFO_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {Config.DEPLOYMENT_INFO_FILE} not found. Run deploy.py first.")
        return None
    except Exception as e:
        print(f"❌ Error loading deployment info: {e}")
        return None

def cleanup_runtime(deployment_info):
    """Clean up AgentCore Runtime and ECR"""
    print("🚀 Cleaning up AgentCore Runtime...")
    
    region = Config.AWS_REGION
    agentcore_client = boto3.client('bedrock-agentcore-control', region_name=region)
    ecr_client = boto3.client('ecr', region_name=region)
    
    # Delete runtime if exists in deployment info
    if 'runtime' in deployment_info and 'agent_arn' in deployment_info['runtime']:
        agent_arn = deployment_info['runtime']['agent_arn']
        agent_id = agent_arn.split('/')[-1]
        try:
            agentcore_client.delete_agent_runtime(agentRuntimeId=agent_id)
            print(f"✅ Runtime deleted: {agent_id}")
        except Exception as e:
            print(f"⚠️ Could not delete runtime {agent_id}: {e}")
    
    # Delete ECR repository
    try:
        repo_name = f"bedrock-agentcore-{Config.AGENT_NAME}"
        ecr_client.delete_repository(repositoryName=repo_name, force=True)
        print(f"✅ ECR repository deleted: {repo_name}")
    except ecr_client.exceptions.RepositoryNotFoundException:
        print("ℹ️ ECR repository not found")
    except Exception as e:
        print(f"⚠️ Could not delete ECR repository: {e}")
    
    # Try Runtime toolkit cleanup as fallback
    try:
        from bedrock_agentcore_starter_toolkit import Runtime
        runtime = Runtime()
        runtime.destroy(delete_ecr_repo=False)  # ECR already handled above
        print("✅ Runtime toolkit cleanup completed")
    except Exception as e:
        print(f"⚠️ Runtime toolkit cleanup warning: {e}")

def cleanup_gateway(deployment_info):
    """Clean up AgentCore Gateway and targets"""
    print("🌐 Cleaning up AgentCore Gateway...")
    
    region = Config.AWS_REGION
    agentcore_client = boto3.client('bedrock-agentcore-control', region_name=region)
    
    if 'gateway' in deployment_info:
        gateway_id = deployment_info['gateway']['gateway_id']
        
        # Skip deletion of shared/existing gateway
        if gateway_id == "customer-support-gatewat-allz9rxw5k":
            print("ℹ️ Skipping deletion of shared gateway")
        else:
            # List and delete targets first
            try:
                targets = agentcore_client.list_gateway_targets(gatewayIdentifier=gateway_id)
                for target in targets.get('items', []):
                    target_id = target.get('targetId') or target.get('id')
                    target_name = target.get('name', target_id)
                    try:
                        agentcore_client.delete_gateway_target(
                            gatewayIdentifier=gateway_id,
                            targetId=target_id
                        )
                        print(f"✅ Deleted gateway target: {target_name}")
                    except Exception as e:
                        print(f"⚠️ Could not delete target {target_name}: {e}")
            except Exception as e:
                print(f"⚠️ Target cleanup warning: {e}")
            
            # Delete gateway
            try:
                agentcore_client.delete_gateway(gatewayIdentifier=gateway_id)
                print(f"✅ Gateway deleted: {gateway_id}")
            except Exception as e:
                print(f"⚠️ Could not delete gateway {gateway_id}: {e}")
    
    # Clean up IAM role created for gateway
    if 'gateway' in deployment_info and 'gateway_role_arn' in deployment_info['gateway']:
        try:
            iam_client = boto3.client('iam', region_name=region)
            role_arn = deployment_info['gateway']['gateway_role_arn']
            role_name = role_arn.split('/')[-1]
            
            # Delete inline policy first
            try:
                iam_client.delete_role_policy(RoleName=role_name, PolicyName="GatewayPolicy")
            except Exception:
                pass
            
            # Delete role
            iam_client.delete_role(RoleName=role_name)
            print(f"✅ Gateway IAM role deleted: {role_name}")
        except Exception as e:
            print(f"⚠️ Could not delete gateway IAM role: {e}")

def cleanup_s3(deployment_info):
    """Clean up S3 bucket and objects"""
    print("📦 Cleaning up S3 bucket...")
    
    region = Config.AWS_REGION
    s3_client = boto3.client('s3', region_name=region)
    
    if 's3' in deployment_info and 'bucket_name' in deployment_info['s3']:
        bucket_name = deployment_info['s3']['bucket_name']
        
        try:
            # Delete all objects first
            try:
                objects = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in objects:
                    for obj in objects['Contents']:
                        s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                        print(f"✅ Deleted object: {obj['Key']}")
            except s3_client.exceptions.NoSuchBucket:
                print(f"ℹ️ S3 bucket not found: {bucket_name}")
                return
            except Exception as e:
                print(f"⚠️ Object deletion warning: {e}")
            
            # Delete bucket
            try:
                s3_client.delete_bucket(Bucket=bucket_name)
                print(f"✅ S3 bucket deleted: {bucket_name}")
            except s3_client.exceptions.NoSuchBucket:
                print(f"ℹ️ S3 bucket already deleted: {bucket_name}")
            except Exception as e:
                print(f"⚠️ Could not delete S3 bucket: {e}")
                
        except Exception as e:
            print(f"⚠️ S3 cleanup warning: {e}")
    else:
        print("ℹ️ No S3 bucket information found")

def cleanup_cloudformation(deployment_info):
    """Clean up CloudFormation stack"""
    print("📋 Cleaning up CloudFormation stack...")
    
    region = Config.AWS_REGION
    cf_client = boto3.client('cloudformation', region_name=region)
    stack_name = Config.STACK_NAME
    
    try:
        # Check if stack exists
        try:
            cf_client.describe_stacks(StackName=stack_name)
        except cf_client.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                print(f"ℹ️ CloudFormation stack not found: {stack_name}")
                return
            raise
        
        # Delete stack
        cf_client.delete_stack(StackName=stack_name)
        print(f"⏳ Deleting CloudFormation stack: {stack_name}")
        
        # Wait for deletion with timeout
        try:
            waiter = cf_client.get_waiter('stack_delete_complete')
            waiter.wait(StackName=stack_name, WaiterConfig={'Delay': 30, 'MaxAttempts': 20})
            print(f"✅ CloudFormation stack deleted: {stack_name}")
        except Exception as e:
            print(f"⚠️ Stack deletion may still be in progress: {e}")
        
    except Exception as e:
        print(f"⚠️ CloudFormation cleanup warning: {e}")

def cleanup_local_files():
    """Clean up local deployment files"""
    print("🧹 Cleaning up local files...")
    
    files_to_remove = [
        Config.DEPLOYMENT_INFO_FILE,
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
    print(f"  - CloudFormation stack: {Config.STACK_NAME}")
    
    confirm = input("\nAre you sure you want to proceed? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cleanup cancelled.")
        return 0
    
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
    
    print("\n🎉 Cleanup completed!")
    print("All AgentCore resources have been processed.")
    
    return 0

if __name__ == "__main__":
    exit(main())
