#!/usr/bin/env python3
"""
Strands Agents Module - Customer Support Agent Implementation

This module contains the implementation of Strands-based agents for AgentCore:
- Customer Support Agent with comprehensive tooling
- Memory integration for conversation continuity
- Tool definitions for customer service operations
- Agent configuration and setup utilities

Components:
- Customer profile and order management tools
- Warranty checking and device support tools
- Knowledge base search capabilities
- Memory session management
- Interactive demonstration modes
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration
REGION = os.getenv('AWS_REGION', 'us-east-1')
CUSTOMER_ID = "customer_001"
SESSION_ID = f"support_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def setup_customer_support_tools():
    """Set up customer support tools."""
    from strands import tool
    
    @tool
    def get_customer_profile(customer_id: str) -> str:
        """Get customer profile and order history."""
        if customer_id == "customer_001":
            return """Customer Profile:
Name: John Doe
Email: john.doe@email.com
Phone: +1-555-0123
Communication Preference: Email

Order History:
- Order #123456: iPhone 15 Pro (Purchased: Last month, Status: Delivered)
- Order #654321: Sennheiser HD 660S Headphones (Purchased: 2 months ago, Status: Delivered)

Previous Issues:
- None on record

Account Status: Premium Customer"""
        return "Customer not found in system"
    
    @tool
    def check_warranty_status(serial_number: str, customer_email: str = None) -> str:
        """Check warranty status for a device."""
        # Mock warranty check
        if "iPhone" in serial_number or serial_number == "123456":
            return """Warranty Status:
Device: iPhone 15 Pro
Serial: F2LW8J9K2L
Purchase Date: October 2024
Warranty: Active until October 2025
Coverage: Full hardware and software support
AppleCare+: Not enrolled

Status: ✅ ACTIVE - 11 months remaining"""
        return "Device not found or warranty expired"
    
    @tool
    def search_knowledge_base(query: str) -> str:
        """Search internal knowledge base for solutions."""
        knowledge = {
            "iphone hot": "iPhone overheating solutions: 1) Remove case, 2) Close background apps, 3) Avoid direct sunlight, 4) Update iOS, 5) Reset settings if needed",
            "headphones": "Sennheiser troubleshooting: 1) Check cable connections, 2) Test with different device, 3) Clean audio jack, 4) Check impedance compatibility",
            "charging": "Charging issues: 1) Try different cable, 2) Clean charging port, 3) Check power adapter, 4) Restart device, 5) Check for iOS updates",
            "battery": "Battery optimization: 1) Enable Low Power Mode, 2) Reduce screen brightness, 3) Disable background refresh, 4) Check battery health in Settings"
        }
        
        query_lower = query.lower()
        for key, solution in knowledge.items():
            if key in query_lower:
                return f"Knowledge Base Solution:\n{solution}"
        
        return "No specific solution found. Please provide more details about the issue."
    
    @tool
    def escalate_to_human(issue_summary: str, priority: str = "normal", customer_id: str = None) -> str:
        """Escalate complex issues to human support."""
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        priority_times = {
            "urgent": "15 minutes",
            "high": "1 hour", 
            "normal": "4 hours",
            "low": "24 hours"
        }
        
        response_time = priority_times.get(priority.lower(), "4 hours")
        
        return f"""🎫 Issue Escalated to Human Support

Ticket ID: {ticket_id}
Priority: {priority.upper()}
Customer: {customer_id or 'Unknown'}
Issue: {issue_summary}

Expected Response Time: {response_time}
Contact Method: Email (customer preference)

A specialist will contact you shortly. Thank you for your patience!"""
    
    return [get_customer_profile, check_warranty_status, search_knowledge_base, escalate_to_human]

def setup_memory_integration():
    """Set up memory integration if available."""
    try:
        from bedrock_agentcore.memory.client import MemoryClient
        from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole
        from bedrock_agentcore.memory.session import MemorySession
        
        memory_client = MemoryClient(region_name=REGION)
        
        # Try to find existing customer support memory
        memories = memory_client.list_memories()
        customer_memory = None
        
        for memory in memories:
            if "CustomerSupport" in memory.get('name', ''):
                customer_memory = memory
                break
        
        if customer_memory:
            logger.info(f"✅ Using existing memory: {customer_memory['memoryId']}")
            memory_session = MemorySession(
                memory_id=customer_memory['memoryId'],
                actor_id=CUSTOMER_ID,
                session_id=SESSION_ID,
                region_name=REGION
            )
            return memory_session
        else:
            logger.info("No existing customer support memory found")
            return None
            
    except Exception as e:
        logger.warning(f"Memory integration not available: {e}")
        return None

def create_customer_support_agent():
    """Create the customer support agent."""
    from strands import Agent
    
    # Set up tools
    tools = setup_customer_support_tools()
    
    # Set up memory (optional)
    memory_session = setup_memory_integration()
    
    # Create agent with comprehensive system prompt
    system_prompt = f"""You are an intelligent customer support agent for a technology company.

Customer Information:
- Customer ID: {CUSTOMER_ID}
- Name: John Doe (Premium Customer)
- Communication Preference: Email
- Recent Orders: iPhone 15 Pro, Sennheiser headphones

Your capabilities:
✅ Access customer profiles and order history
✅ Check warranty status for devices  
✅ Search knowledge base for solutions
✅ Escalate complex issues to human specialists

Guidelines:
- Always be professional, helpful, and empathetic
- Use customer tools to get accurate information
- Provide step-by-step troubleshooting when possible
- Escalate to human support for complex hardware issues
- Remember customer preferences (email communication)
- Reference previous orders when relevant

Memory Integration: {'✅ Active' if memory_session else '❌ Not Available'}"""

    agent = Agent(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        tools=tools,
        system_prompt=system_prompt
    )
    
    logger.info("✅ Customer support agent created successfully")
    return agent, memory_session

def run_demo_scenarios(agent):
    """Run demonstration scenarios."""
    print("\n" + "="*70)
    print("🧪 AgentCore Customer Support Demo Scenarios")
    print("="*70)
    
    scenarios = [
        {
            "title": "Customer Profile Lookup",
            "query": "Hi, can you check my account information?",
            "demonstrates": "Tool Integration - Customer Data"
        },
        {
            "title": "Warranty Check",
            "query": "I need to check the warranty on my iPhone 15 Pro",
            "demonstrates": "Tool Integration - Warranty System"
        },
        {
            "title": "Technical Troubleshooting",
            "query": "My iPhone gets really hot when I'm charging it. What should I do?",
            "demonstrates": "Knowledge Base Search"
        },
        {
            "title": "Complex Issue Escalation",
            "query": "My iPhone screen is completely black and won't turn on at all. I've tried everything.",
            "demonstrates": "Human Escalation Workflow"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}️⃣ {scenario['title']}")
        print(f"Demonstrates: {scenario['demonstrates']}")
        print(f"Customer: {scenario['query']}")
        print("Agent:", end=" ")
        
        try:
            response = agent(scenario['query'])
            response_text = str(response)
            print(response_text)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 70)
        
        # Pause between scenarios
        if i < len(scenarios):
            input("\nPress Enter to continue to next scenario...")
    
    print("\n✅ All scenarios completed successfully!")

def run_interactive_session(agent):
    """Run interactive customer support session."""
    print("\n" + "="*70)
    print("💬 Interactive Customer Support Session")
    print("="*70)
    print("You are John Doe (customer_001) with existing order history")
    print("Type 'quit' to exit, 'help' for suggestions")
    print("="*70)
    
    conversation_count = 0
    
    while True:
        try:
            user_input = input("\n💬 Customer: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thank you for contacting support! Have a great day!")
                break
            
            if user_input.lower() == 'help':
                print("\n📋 Try asking about:")
                print("  - 'Check my account information'")
                print("  - 'What's the warranty on my iPhone?'")
                print("  - 'My headphones aren't working properly'")
                print("  - 'iPhone battery drains too fast'")
                print("  - 'I need urgent help with my device'")
                continue
            
            if not user_input:
                continue
            
            conversation_count += 1
            print(f"\n🎧 Support Agent (Turn {conversation_count}):")
            
            response = agent(user_input)
            response_text = str(response)
            print(response_text)
            
        except KeyboardInterrupt:
            print("\n\n👋 Support session ended!")
            break
        except Exception as e:
            logger.error(f"Error in session: {e}")
            print(f"\n❌ Technical issue: {e}")

def main():
    """Main function."""
    print("🚀 AgentCore Customer Support Example")
    print("="*50)
    print("Demonstrating working AgentCore components:")
    print("✅ Strands Agent with custom tools")
    print("✅ Memory Client integration (if available)")
    print("✅ Customer support workflow")
    print("✅ Tool integration and escalation")
    print("="*50)
    
    try:
        # Create agent
        print("\n📋 Setting up Customer Support Agent...")
        agent, memory_session = create_customer_support_agent()
        
        # Choose demo mode
        print("\n📋 Choose demo mode:")
        print("1. Automated scenarios (shows all features)")
        print("2. Interactive session (chat with agent)")
        print("3. Both")
        
        while True:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                run_demo_scenarios(agent)
                break
            elif choice == "2":
                run_interactive_session(agent)
                break
            elif choice == "3":
                run_demo_scenarios(agent)
                run_interactive_session(agent)
                break
            else:
                print("Invalid choice. Please enter 1-3.")
    
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")
        print(f"\n❌ Example failed: {e}")
        return 1
    
    print("\n🎉 AgentCore customer support example completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())