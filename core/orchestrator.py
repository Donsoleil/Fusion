#!/usr/bin/env python3
"""
Core Orchestrator - Fusion v15
Handles prompt rewriting and agent selection
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from agents.prompt_master_agent import PromptMasterAgent

class Orchestrator:
    """
    Core orchestrator for prompt rewriting and agent selection
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Orchestrator")
        self.prompt_master = PromptMasterAgent()
        
        # Agent routing map based on prompt patterns
        self.agent_routing = {
            "design": ["vp_design", "creative_director", "principal_designer"],
            "strategy": ["strategy_pilot", "vp_of_product", "market_analyst"],
            "technical": ["design_technologist", "component_librarian"],
            "content": ["content_designer", "deck_narrator"],
            "evaluation": ["evaluator", "feedback_amplifier"],
            "general": ["evaluator", "vp_design"]
        }
        
    async def rewrite(self, prompt: str) -> str:
        """
        Rewrite prompt using PromptMaster
        
        Args:
            prompt: Original user prompt
            
        Returns:
            Rewritten/enhanced prompt
        """
        try:
            result = await self.prompt_master.run_async(prompt, {})
            
            if isinstance(result, dict):
                # Check for rewritten prompt in shared state
                shared_state = result.get("shared_state", {})
                rewritten = shared_state.get("rewritten_prompt")
                
                if rewritten:
                    return rewritten
                    
                # Fallback to output or enhanced_output
                return result.get("enhanced_output", result.get("output", prompt))
            
            return str(result)
            
        except Exception as e:
            self.logger.error(f"Prompt rewriting failed: {e}")
            return prompt
    
    def select_agent(self, prompt: str) -> str:
        """
        Select best agent based on prompt analysis
        
        Args:
            prompt: Input prompt (potentially rewritten)
            
        Returns:
            Selected agent name
        """
        prompt_lower = prompt.lower()
        
        # Simple keyword-based routing
        if any(word in prompt_lower for word in ["design", "ui", "ux", "interface", "visual"]):
            return "vp_design"
        elif any(word in prompt_lower for word in ["strategy", "roadmap", "business", "plan"]):
            return "strategy_pilot"
        elif any(word in prompt_lower for word in ["code", "technical", "implement", "development"]):
            return "design_technologist"
        elif any(word in prompt_lower for word in ["content", "copy", "text", "narrative"]):
            return "content_designer"
        elif any(word in prompt_lower for word in ["evaluate", "analyze", "review", "critique"]):
            return "evaluator"
        else:
            return "evaluator"  # Default fallback

# Global orchestrator instance
orchestrator = Orchestrator()