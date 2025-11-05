"""
Memory Helper Functions for AgentCore Examples

This module provides utility functions for AgentCore Memory management,
including memory creation, strategy configuration, and session management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
from bedrock_agentcore_starter_toolkit.operations.memory.models.strategies import (
    SemanticStrategy, SummaryStrategy, CustomSemanticStrategy, 
    CustomSummaryStrategy, CustomUserPreferenceStrategy,
    ExtractionConfig, ConsolidationConfig
)
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole
from bedrock_agentcore.memory.session import MemorySession, MemorySessionManager

logger = logging.getLogger(__name__)

# Message role constants
USER = MessageRole.USER
ASSISTANT = MessageRole.ASSISTANT


def create_short_term_memory(
    memory_name: str,
    region: str = "us-east-1",
    description: str = "Short-term memory for conversation continuity"
) -> str:
    """
    Create a short-term memory resource for conversation continuity.
    
    Args:
        memory_name: Name for the memory resource
        region: AWS region
        description: Description of the memory resource
    
    Returns:
        Memory ID
    """
    memory_manager = MemoryManager(region_name=region)
    
    try:
        # Create memory without strategies for short-term storage
        memory = memory_manager.get_or_create_memory(
            name=memory_name,
            strategies=[],  # No strategies for raw conversation storage
            description=description,
            event_expiry_days=7  # Short retention for STM
        )
        
        logger.info(f"✅ Created short-term memory: {memory.id}")
        return memory.id
        
    except Exception as e:
        logger.error(f"❌ Failed to create short-term memory: {e}")
        raise


def create_long_term_memory(
    memory_name: str,
    memory_execution_role_arn: str,
    region: str = "us-east-1",
    description: str = "Long-term memory with semantic and preference strategies"
) -> str:
    """
    Create a long-term memory resource with multiple strategies.
    
    Args:
        memory_name: Name for the memory resource
        memory_execution_role_arn: IAM role ARN for custom strategies
        region: AWS region
        description: Description of the memory resource
    
    Returns:
        Memory ID
    """
    memory_manager = MemoryManager(region_name=region)
    
    # Define memory strategies
    strategies = [
        CustomSemanticStrategy(
            name="SemanticMemory",
            description="Stores factual information from conversations",
            extraction_config=ExtractionConfig(
                append_to_prompt="Extract factual information and key insights from the conversation",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            consolidation_config=ConsolidationConfig(
                append_to_prompt="Consolidate and organize semantic information",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            namespaces=["semantic/{actorId}"]
        ),
        CustomUserPreferenceStrategy(
            name="UserPreferences",
            description="Captures user preferences and behavior patterns",
            extraction_config=ExtractionConfig(
                append_to_prompt="Extract user preferences, interests, and behavior patterns",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            consolidation_config=ConsolidationConfig(
                append_to_prompt="Consolidate user preferences and update user profile",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            namespaces=["preferences/{actorId}"]
        ),
        CustomSummaryStrategy(
            name="ConversationSummary",
            description="Maintains conversation summaries for context",
            extraction_config=ExtractionConfig(
                append_to_prompt="Summarize the key points and outcomes of the conversation",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            consolidation_config=ConsolidationConfig(
                append_to_prompt="Update and maintain conversation summary",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            namespaces=["summary/{actorId}"]
        )
    ]
    
    try:
        memory = memory_manager.get_or_create_memory(
            name=memory_name,
            strategies=strategies,
            description=description,
            event_expiry_days=90,  # Longer retention for LTM
            memory_execution_role_arn=memory_execution_role_arn
        )
        
        logger.info(f"✅ Created long-term memory with {len(strategies)} strategies: {memory.id}")
        return memory.id
        
    except Exception as e:
        logger.error(f"❌ Failed to create long-term memory: {e}")
        raise


def create_customer_support_memory(
    memory_name: str,
    memory_execution_role_arn: str,
    region: str = "us-east-1"
) -> str:
    """
    Create specialized memory for customer support use case.
    
    Args:
        memory_name: Name for the memory resource
        memory_execution_role_arn: IAM role ARN for custom strategies
        region: AWS region
    
    Returns:
        Memory ID
    """
    memory_manager = MemoryManager(region_name=region)
    
    # Customer support specific strategies
    strategies = [
        CustomSemanticStrategy(
            name="CustomerSupportSemantic",
            description="Stores customer issues, orders, and product information",
            extraction_config=ExtractionConfig(
                append_to_prompt="Extract customer issues, order details, product information, and resolution steps",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            consolidation_config=ConsolidationConfig(
                append_to_prompt="Consolidate customer support information and maintain customer history",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            namespaces=["support/customer/{actorId}/semantic"]
        ),
        CustomUserPreferenceStrategy(
            name="CustomerPreferences",
            description="Captures customer preferences and communication style",
            extraction_config=ExtractionConfig(
                append_to_prompt="Extract customer preferences, communication style, and service expectations",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            consolidation_config=ConsolidationConfig(
                append_to_prompt="Update customer preference profile for personalized service",
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            namespaces=["support/customer/{actorId}/preferences"]
        )
    ]
    
    try:
        memory = memory_manager.get_or_create_memory(
            name=memory_name,
            strategies=strategies,
            description="Memory for customer support agent with issue tracking and preferences",
            event_expiry_days=365,  # Long retention for customer history
            memory_execution_role_arn=memory_execution_role_arn
        )
        
        logger.info(f"✅ Created customer support memory: {memory.id}")
        return memory.id
        
    except Exception as e:
        logger.error(f"❌ Failed to create customer support memory: {e}")
        raise


def create_memory_session(
    memory_id: str,
    actor_id: str,
    session_id: str,
    region: str = "us-east-1"
) -> MemorySession:
    """
    Create a memory session for a specific actor and session.
    
    Args:
        memory_id: Memory resource ID
        actor_id: Unique identifier for the actor (user/customer)
        session_id: Unique identifier for the session
        region: AWS region
    
    Returns:
        MemorySession instance
    """
    try:
        session_manager = MemorySessionManager(
            memory_id=memory_id,
            region_name=region
        )
        
        memory_session = session_manager.create_memory_session(
            actor_id=actor_id,
            session_id=session_id
        )
        
        logger.info(f"✅ Created memory session for actor {actor_id}, session {session_id}")
        return memory_session
        
    except Exception as e:
        logger.error(f"❌ Failed to create memory session: {e}")
        raise


def seed_conversation_history(
    memory_session: MemorySession,
    conversations: List[Dict[str, str]]
) -> None:
    """
    Seed memory session with previous conversation history.
    
    Args:
        memory_session: MemorySession instance
        conversations: List of conversation turns with 'role' and 'content' keys
    """
    try:
        messages = []
        for conv in conversations:
            role = USER if conv['role'] == 'user' else ASSISTANT
            messages.append(ConversationalMessage(conv['content'], role))
        
        if messages:
            result = memory_session.add_turns(messages)
            logger.info(f"✅ Seeded {len(messages)} conversation turns, event ID: {result['eventId']}")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed conversation history: {e}")
        raise


def get_conversation_context(
    memory_session: MemorySession,
    query: str,
    max_turns: int = 10,
    namespace_prefix: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant conversation context for a query.
    
    Args:
        memory_session: MemorySession instance
        query: User query to find relevant context for
        max_turns: Maximum number of conversation turns to retrieve
        namespace_prefix: Optional namespace to filter memories
    
    Returns:
        List of relevant memory records
    """
    try:
        # Get recent conversation turns
        recent_turns = memory_session.get_last_k_turns(k=max_turns)
        
        # Search long-term memories if namespace provided
        long_term_memories = []
        if namespace_prefix:
            long_term_memories = memory_session.search_long_term_memories(
                query=query,
                namespace_prefix=namespace_prefix,
                top_k=5
            )
        
        # Combine and format context
        context = []
        
        # Add recent conversation context
        for turn in recent_turns:
            context.append({
                'type': 'conversation',
                'content': turn.get('content', {}),
                'timestamp': turn.get('timestamp'),
                'role': turn.get('role')
            })
        
        # Add long-term memory context
        for memory in long_term_memories:
            context.append({
                'type': 'memory',
                'content': memory.get('content', {}),
                'score': memory.get('score', 0),
                'namespace': memory.get('namespace')
            })
        
        logger.info(f"✅ Retrieved {len(context)} context items for query")
        return context
        
    except Exception as e:
        logger.error(f"❌ Failed to get conversation context: {e}")
        return []


def format_memory_context(context: List[Dict[str, Any]], max_length: int = 2000) -> str:
    """
    Format memory context for injection into agent prompts.
    
    Args:
        context: List of context items from get_conversation_context
        max_length: Maximum length of formatted context
    
    Returns:
        Formatted context string
    """
    if not context:
        return ""
    
    formatted_lines = []
    current_length = 0
    
    # Sort by relevance (memories first, then recent conversations)
    sorted_context = sorted(context, key=lambda x: (
        x['type'] == 'conversation',  # Memories first
        -x.get('score', 0) if x['type'] == 'memory' else 0
    ))
    
    for item in sorted_context:
        if current_length >= max_length:
            break
        
        if item['type'] == 'memory':
            content = item['content'].get('text', '')
            score = item.get('score', 0)
            line = f"[Memory - Score: {score:.2f}] {content[:200]}..."
        else:
            content = item['content'].get('text', '')
            role = item.get('role', 'unknown')
            line = f"[{role.title()}] {content[:150]}..."
        
        if current_length + len(line) <= max_length:
            formatted_lines.append(line)
            current_length += len(line)
    
    return "\n".join(formatted_lines)


def cleanup_memory_resources(
    memory_ids: List[str],
    region: str = "us-east-1"
) -> None:
    """
    Clean up memory resources.
    
    Args:
        memory_ids: List of memory IDs to delete
        region: AWS region
    """
    memory_manager = MemoryManager(region_name=region)
    
    for memory_id in memory_ids:
        try:
            memory_manager.delete_memory(memory_id)
            logger.info(f"✅ Deleted memory resource: {memory_id}")
        except Exception as e:
            logger.error(f"❌ Failed to delete memory {memory_id}: {e}")


# Customer support memory configuration
CUSTOMER_SUPPORT_MEMORY_CONFIG = {
    "strategies": [
        {
            "type": "semantic",
            "name": "SupportHistory",
            "description": "Customer issues and resolutions",
            "namespaces": ["support/{actorId}/history"]
        },
        {
            "type": "user_preference",
            "name": "CustomerProfile",
            "description": "Customer preferences and communication style",
            "namespaces": ["support/{actorId}/profile"]
        }
    ],
    "retention_days": 365
}


def get_customer_support_memory_config() -> Dict[str, Any]:
    """Get optimized memory configuration for customer support use case."""
    return CUSTOMER_SUPPORT_MEMORY_CONFIG.copy()
