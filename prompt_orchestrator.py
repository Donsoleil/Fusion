#!/usr/bin/env python3
"""
Prompt Orchestrator Service - Fusion v15
Dedicated microservice for prompt analysis, rewriting, and agent routing
Extracted from PromptMaster agent for scalable architecture
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Import PromptMaster functionality
from agents.prompt_master_agent import PromptMasterAgent

app = FastAPI(title="Fusion Prompt Orchestrator", version="15.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PromptRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = {}
    agent_preference: Optional[str] = None
    use_memory: bool = True
    use_fallback: bool = True

class PromptResponse(BaseModel):
    original_prompt: str
    rewritten_prompt: str
    pattern_type: str
    confidence: float
    suggested_agents: List[str]
    fallback_needed: bool
    memory_insights: Dict[str, Any]
    execution_time: float
    enhanced_output: str

class AgentRouteRequest(BaseModel):
    prompt: str
    confidence_threshold: float = 0.7

class AgentRouteResponse(BaseModel):
    recommended_agent: str
    confidence: float
    alternatives: List[str]
    reasoning: str

# Initialize PromptMaster
prompt_master = PromptMasterAgent()

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Fusion Prompt Orchestrator",
        "version": "15.0.0",
        "description": "Dedicated microservice for prompt analysis, rewriting, and agent routing",
        "endpoints": [
            "/rewrite - Analyze and rewrite prompts",
            "/route - Get agent routing recommendations", 
            "/patterns - Get available prompt patterns",
            "/health - Service health check"
        ]
    }

@app.post("/rewrite", response_model=PromptResponse)
async def rewrite_prompt(req: PromptRequest):
    """
    Analyze and rewrite a prompt using PromptMaster logic
    
    Args:
        req: PromptRequest containing prompt and options
        
    Returns:
        PromptResponse with analysis results and rewritten prompt
    """
    try:
        start_time = time.time()
        
        # Use PromptMaster to analyze and rewrite
        result = await prompt_master.run_async(req.prompt, req.context)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Extract data from PromptMaster response
        shared_state = result.get("shared_state", {})
        
        response = PromptResponse(
            original_prompt=req.prompt,
            rewritten_prompt=shared_state.get("rewritten_prompt", req.prompt),
            pattern_type=shared_state.get("pattern_type", "general"),
            confidence=result.get("confidence", 0.0),
            suggested_agents=shared_state.get("suggested_agents", []),
            fallback_needed=shared_state.get("fallback_needed", False),
            memory_insights=shared_state.get("memory_insights", {}),
            execution_time=time.time() - start_time,
            enhanced_output=result.get("enhanced_output", "")
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt rewriting failed: {str(e)}")

@app.post("/route", response_model=AgentRouteResponse)
async def route_agent(req: AgentRouteRequest):
    """
    Get agent routing recommendations based on prompt analysis
    
    Args:
        req: AgentRouteRequest with prompt and confidence threshold
        
    Returns:
        AgentRouteResponse with recommended agent and alternatives
    """
    try:
        # Use PromptMaster for pattern analysis
        result = await prompt_master.run_async(req.prompt, {})
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        shared_state = result.get("shared_state", {})
        suggested_agents = shared_state.get("suggested_agents", [])
        confidence = result.get("confidence", 0.0)
        pattern_type = shared_state.get("pattern_type", "general")
        
        # Determine primary recommendation
        if suggested_agents and confidence >= req.confidence_threshold:
            recommended_agent = suggested_agents[0]
            alternatives = suggested_agents[1:3]  # Next 2 alternatives
        else:
            # Default routing based on pattern
            pattern_defaults = {
                "design_focused": "vp_design",
                "strategy_focused": "strategy_pilot", 
                "technical_focused": "design_technologist",
                "content_focused": "content_designer",
                "general": "evaluator"
            }
            recommended_agent = pattern_defaults.get(pattern_type, "evaluator")
            alternatives = ["vp_design", "creative_director"]
        
        reasoning = f"Pattern '{pattern_type}' detected with {confidence:.2f} confidence. "
        if confidence >= req.confidence_threshold:
            reasoning += "High confidence routing to specialized agents."
        else:
            reasoning += "Low confidence, using fallback routing."
        
        return AgentRouteResponse(
            recommended_agent=recommended_agent,
            confidence=confidence,
            alternatives=alternatives,
            reasoning=reasoning
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent routing failed: {str(e)}")

@app.get("/patterns")
async def get_patterns():
    """Get available prompt patterns and their configurations"""
    try:
        patterns = await prompt_master._read_patterns()
        return {
            "patterns": patterns.get("patterns", {}),
            "total_patterns": len(patterns.get("patterns", {}))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

@app.get("/health")
async def health_check():
    """Service health check"""
    try:
        # Test PromptMaster functionality
        test_result = await prompt_master._analyze_prompt_pattern("test prompt")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "prompt_master_available": True,
            "memory_files_exist": {
                "agent_memory": os.path.exists(prompt_master.memory_file),
                "pattern_registry": os.path.exists(prompt_master.pattern_file)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/analyze")
async def analyze_prompt(req: PromptRequest):
    """
    Lightweight prompt analysis without rewriting
    For quick pattern detection and agent suggestions
    """
    try:
        pattern, confidence, suggested_agents = await prompt_master._analyze_prompt_pattern(req.prompt)
        insights = await prompt_master._get_memory_insights(req.prompt)
        
        return {
            "pattern": pattern,
            "confidence": confidence, 
            "suggested_agents": suggested_agents,
            "memory_insights": {
                "similar_prompts_count": len(insights["similar_prompts"]),
                "successful_patterns_count": len(insights["successful_patterns"]),
                "fallback_triggers_count": len(insights["fallback_triggers"])
            },
            "fallback_needed": confidence < 0.7
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt analysis failed: {str(e)}")

# Configuration endpoint for updating patterns
@app.post("/patterns/update")
async def update_patterns(patterns: Dict[str, Any]):
    """Update prompt patterns configuration"""
    try:
        # Validate pattern structure
        if "patterns" not in patterns:
            raise HTTPException(status_code=400, detail="Invalid pattern structure")
        
        # Write to pattern file
        with open(prompt_master.pattern_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        return {
            "message": "Patterns updated successfully",
            "patterns_count": len(patterns.get("patterns", {}))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern update failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Fusion Prompt Orchestrator Service")
    print("📍 Available at: http://localhost:8001")
    print("📋 API docs at: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)