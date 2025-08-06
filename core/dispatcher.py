#!/usr/bin/env python3
"""
Core Dispatcher - Fusion v15
Proper agent dispatch system replacing direct agent calls
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from core.agent_loader import load_agents

class Dispatcher:
    """
    Core dispatcher for routing requests to agents
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Dispatcher")
        self.agents = load_agents()
        
    async def dispatch(self, agent_name: str, input_text: str, context: Dict[str, Any] = None) -> str:
        """
        Dispatch input to specified agent and return result
        
        Args:
            agent_name: Name of the agent to dispatch to
            input_text: Input text/prompt
            context: Optional context dictionary
            
        Returns:
            String output from the agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found. Available: {list(self.agents.keys())}")
            
        agent = self.agents[agent_name]
        
        try:
            # Try async run method first
            if hasattr(agent, 'run_async'):
                result = await agent.run_async(input_text, context or {})
                # Handle both dict and string responses
                if isinstance(result, dict):
                    return result.get('output', result.get('enhanced_output', str(result)))
                return str(result)
                
            # Try regular run method
            elif hasattr(agent, 'run'):
                result = await agent.run(input_text, context or {})
                if isinstance(result, dict):
                    return result.get('output', result.get('enhanced_output', str(result)))
                return str(result)
                
            # Fallback to calling agent directly
            else:
                result = agent(input_text)
                return str(result)
                
        except Exception as e:
            self.logger.error(f"Error dispatching to {agent_name}: {e}")
            raise
            
    def list_agents(self) -> Dict[str, str]:
        """List all available agents with their types"""
        return {name: type(agent).__name__ for name, agent in self.agents.items()}

# Global dispatcher instance
dispatcher = Dispatcher()