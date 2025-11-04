#!/usr/bin/env python3
"""
Run queries using the working example
"""

import sys
import os
sys.path.append('.')
sys.path.append('./agents')

def run_queries_with_example():
    """Run queries using the working example with memory features"""
    
    try:
        from agents.strands_agents import create_customer_support_agent
        
        print("🧪 Running queries with working example + memory features")
        print("=" * 60)
        
        # Create the agent
        agent, memory_session = create_customer_support_agent()
        
        # Memory demonstration queries
        memory_queries = [
            "My name is Alex and I'm interested in learning about AI.",
            "Can you search for the latest AI trends in 2025?",
            "I'm particularly interested in machine learning applications.",
            "What was my name again?"
        ]
        
        # Gateway integration queries  
        gateway_queries = [
            "I have a Gaming Console Pro device, I want to check my warranty status, warranty serial number is MNO33333333.",
            "What is the weather in northern part of the mars?",
            "Hi, can you check my account information?",
            "My iPhone gets hot when charging, help!"
        ]
        
        print("\n🧠 MEMORY FEATURES DEMONSTRATION")
        print("=" * 40)
        print("Testing short-term memory and conversation continuity...")
        
        for i, query in enumerate(memory_queries, 1):
            print(f"\n{i}. Memory Query: {query}")
            print("-" * 50)
            
            try:
                response = agent(query)
                print("Response:")
                print(str(response))
                
                # Show memory context for name recall
                if "name again" in query.lower():
                    print("\n💡 Memory Feature: Agent should recall 'Alex' from earlier conversation")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n\n🌐 GATEWAY INTEGRATION DEMONSTRATION")
        print("=" * 40)
        print("Testing Lambda and OpenAPI targets through gateway...")
        
        for i, query in enumerate(gateway_queries, 1):
            print(f"\n{i}. Gateway Query: {query}")
            print("-" * 50)
            
            try:
                response = agent(query)
                print("Response:")
                print(str(response))
                
                # Show which tools should be used
                if "warranty" in query.lower():
                    print("\n💡 Gateway Feature: Should use Lambda target for warranty check")
                elif "mars" in query.lower():
                    print("\n💡 Gateway Feature: Should use NASA OpenAPI target for Mars weather")
                elif "account" in query.lower():
                    print("\n💡 Gateway Feature: Should use Lambda target for customer profile")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n\n📊 AGENTCORE FEATURES SUMMARY")
        print("=" * 40)
        print("✅ Memory: Conversation continuity and context retention")
        print("✅ Gateway: Lambda functions and OpenAPI integration")
        print("✅ Runtime: Serverless agent deployment")
        print("✅ Tools: Customer support and web search capabilities")
        
        total_queries = len(memory_queries) + len(gateway_queries)
        print(f"\n🏁 Completed running {total_queries} queries demonstrating AgentCore features")
        
    except ImportError as e:
        print(f"Could not import working example: {e}")
        print("Make sure the agents directory exists and strands_agents.py is available")

def run_memory_demonstration():
    """Demonstrate AgentCore memory features specifically"""
    
    try:
        from agents.strands_agents import create_customer_support_agent
        
        print("\n🧠 AgentCore Memory Features Demonstration")
        print("=" * 50)
        
        # Create agent with memory
        agent, memory_session = create_customer_support_agent()
        
        # Memory test scenarios
        memory_scenarios = [
            {
                "query": "My name is Sarah and I work at TechCorp. I'm having issues with my laptop.",
                "description": "Initial context setting - name and company"
            },
            {
                "query": "The laptop is a ThinkPad X1 Carbon, serial number ABC123456.",
                "description": "Device details for memory storage"
            },
            {
                "query": "What's my name and what device am I having issues with?",
                "description": "Memory recall test - should remember Sarah and ThinkPad"
            },
            {
                "query": "I also need help with my iPhone that won't charge.",
                "description": "Additional device context"
            },
            {
                "query": "Can you summarize all my devices and issues?",
                "description": "Comprehensive memory recall test"
            }
        ]
        
        for i, scenario in enumerate(memory_scenarios, 1):
            print(f"\n{i}. Memory Test: {scenario['description']}")
            print(f"Query: {scenario['query']}")
            print("-" * 60)
            
            try:
                response = agent(scenario['query'])
                print("Response:")
                print(str(response))
                
                # Add memory insights
                if "recall" in scenario['description'].lower():
                    print("\n💡 Memory Feature: Testing information retention from previous turns")
                elif "summarize" in scenario['description'].lower():
                    print("\n💡 Memory Feature: Testing comprehensive context aggregation")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n✅ Memory demonstration completed!")
        
    except Exception as e:
        print(f"Memory demonstration failed: {e}")

if __name__ == "__main__":
    print("Choose demonstration mode:")
    print("1. Gateway + Memory queries (default)")
    print("2. Memory features only")
    
    choice = input("Enter choice (1-2, default=1): ").strip() or "1"
    
    if choice == "2":
        run_memory_demonstration()
    else:
        run_queries_with_example()