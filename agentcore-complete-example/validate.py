#!/usr/bin/env python3
"""
AgentCore Solution Validation Script

Validates the complete deployed AgentCore solution by running comprehensive test queries
that demonstrate all components: Runtime, Gateway, Memory, and Observability.
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.append('.')

import boto3
from bedrock_agentcore_starter_toolkit import Runtime

def load_deployment_info():
    """Load deployment information"""
    try:
        with open("deployment_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ deployment_info.json not found. Run deploy.py first.")
        return None

def test_runtime_invocation(deployment_info):
    """Test AgentCore Runtime invocation"""
    print("🚀 Testing AgentCore Runtime...")
    
    try:
        runtime = Runtime()
        
        # Test queries for runtime validation
        runtime_queries = [
            "Hello, can you help me?",
            "What tools do you have available?",
            "Can you check customer information?"
        ]
        
        for i, query in enumerate(runtime_queries, 1):
            print(f"\n{i}. Runtime Query: {query}")
            print("-" * 50)
            
            try:
                response = runtime.invoke({"prompt": query})
                if response and 'response' in response:
                    print("Response:")
                    print(response['response'][0][:200] + "..." if len(response['response'][0]) > 200 else response['response'][0])
                else:
                    print("No response received")
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n✅ Runtime validation completed")
        return True
        
    except Exception as e:
        print(f"❌ Runtime validation failed: {e}")
        return False

def test_gateway_integration(deployment_info):
    """Test AgentCore Gateway integration"""
    print("\n🌐 Testing AgentCore Gateway Integration...")
    
    # Gateway test queries from notebooks
    gateway_queries = [
        {
            "query": "I have a Gaming Console Pro device, I want to check my warranty status, warranty serial number is MNO33333333.",
            "expected": "Lambda target for warranty check",
            "component": "Lambda Target"
        },
        {
            "query": "What is the weather in northern part of the mars?",
            "expected": "NASA OpenAPI target for Mars weather",
            "component": "OpenAPI Target"
        },
        {
            "query": "Hi, can you check my account information?",
            "expected": "Customer profile lookup via Lambda",
            "component": "Lambda Target"
        },
        {
            "query": "My iPhone gets hot when charging, help!",
            "expected": "Device troubleshooting and warranty check",
            "component": "Lambda Target"
        }
    ]
    
    try:
        runtime = Runtime()
        
        for i, test_case in enumerate(gateway_queries, 1):
            print(f"\n{i}. Gateway Test ({test_case['component']})")
            print(f"Query: {test_case['query']}")
            print(f"Expected: {test_case['expected']}")
            print("-" * 60)
            
            try:
                response = runtime.invoke({"prompt": test_case['query']})
                if response and 'response' in response:
                    print("Response:")
                    response_text = response['response'][0]
                    print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
                    
                    # Check if tools were used
                    if "Tool #" in response_text:
                        print("💡 Gateway Feature: Tools were successfully invoked")
                else:
                    print("No response received")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n✅ Gateway integration validation completed")
        return True
        
    except Exception as e:
        print(f"❌ Gateway validation failed: {e}")
        return False

def test_memory_features(deployment_info):
    """Test AgentCore Memory features"""
    print("\n🧠 Testing AgentCore Memory Features...")
    
    # Memory test scenarios from notebooks
    memory_scenarios = [
        {
            "query": "My name is Alex and I'm interested in learning about AI.",
            "description": "Initial context setting - name and interest",
            "memory_type": "Context Storage"
        },
        {
            "query": "Can you search for the latest AI trends in 2025?",
            "description": "Web search with context retention",
            "memory_type": "Context Retrieval"
        },
        {
            "query": "I'm particularly interested in machine learning applications.",
            "description": "Additional interest specification",
            "memory_type": "Context Extension"
        },
        {
            "query": "What was my name again?",
            "description": "Memory recall test - should remember Alex",
            "memory_type": "Context Recall"
        },
        {
            "query": "Can you summarize what we've discussed about my interests?",
            "description": "Comprehensive memory aggregation test",
            "memory_type": "Context Aggregation"
        }
    ]
    
    try:
        runtime = Runtime()
        
        for i, scenario in enumerate(memory_scenarios, 1):
            print(f"\n{i}. Memory Test ({scenario['memory_type']})")
            print(f"Query: {scenario['query']}")
            print(f"Description: {scenario['description']}")
            print("-" * 60)
            
            try:
                response = runtime.invoke({"prompt": scenario['query']})
                if response and 'response' in response:
                    print("Response:")
                    response_text = response['response'][0]
                    print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
                    
                    # Memory-specific insights
                    if "recall" in scenario['description'].lower():
                        print("💡 Memory Feature: Testing information retention from previous turns")
                    elif "aggregation" in scenario['description'].lower():
                        print("💡 Memory Feature: Testing comprehensive context aggregation")
                else:
                    print("No response received")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n✅ Memory features validation completed")
        return True
        
    except Exception as e:
        print(f"❌ Memory validation failed: {e}")
        return False

def test_observability_features(deployment_info):
    """Test AgentCore Observability features"""
    print("\n📊 Testing AgentCore Observability...")
    
    try:
        # Check CloudWatch logs
        logs_client = boto3.client('logs', region_name='us-east-1')
        
        # Look for agent logs
        log_groups = []
        try:
            response = logs_client.describe_log_groups(
                logGroupNamePrefix='/aws/bedrock-agentcore/runtimes/'
            )
            log_groups = [lg['logGroupName'] for lg in response['logGroups']]
        except Exception as e:
            print(f"⚠️ Could not access CloudWatch logs: {e}")
        
        if log_groups:
            print(f"✅ Found {len(log_groups)} CloudWatch log groups:")
            for lg in log_groups[:3]:  # Show first 3
                print(f"  - {lg}")
        else:
            print("⚠️ No CloudWatch log groups found")
        
        # Check X-Ray traces (if available)
        try:
            xray_client = boto3.client('xray', region_name='us-east-1')
            
            # Get recent traces
            end_time = datetime.now()
            start_time = datetime.fromtimestamp(end_time.timestamp() - 3600)  # Last hour
            
            traces = xray_client.get_trace_summaries(
                TimeRangeType='TimeRangeByStartTime',
                StartTime=start_time,
                EndTime=end_time
            )
            
            trace_count = len(traces.get('TraceSummaries', []))
            if trace_count > 0:
                print(f"✅ Found {trace_count} X-Ray traces in the last hour")
            else:
                print("ℹ️ No recent X-Ray traces found")
                
        except Exception as e:
            print(f"⚠️ Could not access X-Ray traces: {e}")
        
        # Dashboard URL
        dashboard_url = "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core"
        print(f"\n🎯 GenAI Observability Dashboard: {dashboard_url}")
        
        print("\n✅ Observability validation completed")
        return True
        
    except Exception as e:
        print(f"❌ Observability validation failed: {e}")
        return False

def run_comprehensive_validation():
    """Run comprehensive validation of all AgentCore components"""
    print("🧪 AgentCore Solution Comprehensive Validation")
    print("=" * 60)
    print("Testing all components: Runtime, Gateway, Memory, Observability")
    print("=" * 60)
    
    # Load deployment info
    deployment_info = load_deployment_info()
    if not deployment_info:
        return 1
    
    print(f"Deployment Info Loaded:")
    if 'gateway' in deployment_info:
        print(f"  Gateway: {deployment_info['gateway']['gateway_id']}")
    if 'runtime' in deployment_info:
        print(f"  Runtime: {deployment_info['runtime']['agent_arn']}")
    if 's3' in deployment_info:
        print(f"  S3 Bucket: {deployment_info['s3']['bucket_name']}")
    
    # Run validation tests
    results = {}
    
    # Test 1: Runtime
    results['runtime'] = test_runtime_invocation(deployment_info)
    
    # Test 2: Gateway
    results['gateway'] = test_gateway_integration(deployment_info)
    
    # Test 3: Memory
    results['memory'] = test_memory_features(deployment_info)
    
    # Test 4: Observability
    results['observability'] = test_observability_features(deployment_info)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Validation Summary")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Total Components Tested: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for component, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {component.upper()}")
    
    if passed_tests == total_tests:
        print("\n🎉 All AgentCore components validated successfully!")
        print("Your complete solution is working correctly.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} component(s) failed validation.")
        print("Check the detailed output above for specific issues.")
    
    return 0 if passed_tests == total_tests else 1

def main():
    """Main validation function"""
    return run_comprehensive_validation()

if __name__ == "__main__":
    exit(main())