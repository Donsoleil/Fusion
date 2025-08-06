# fusion_api.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
import os
import httpx

# Import dynamic agent loader
from core.agent_loader import load_agents, load_plugins

# Import Fusion core components
from fusion_core.memory.agent_memory import AgentMemory
from fusion_core.telemetry.agent_telemetry import AgentTelemetryLogger
from fusion_core.orchestration.multi_agent_orchestrator import MultiAgentOrchestrator

app = FastAPI(title="Fusion v15 API", version="15.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RunRequest(BaseModel):
    agent: str
    input: str
    use_memory: bool = True
    use_telemetry: bool = True
    use_prompt_orchestrator: bool = True

class PromptRequest(BaseModel):
    input: str
    agent_preference: Optional[str] = None
    use_memory: bool = True
    use_telemetry: bool = True
    use_prompt_orchestrator: bool = True

class ParallelRunRequest(BaseModel):
    agents: List[str]
    input: str
    use_evaluator: bool = True

class AgentStatus(BaseModel):
    agent: str
    available: bool
    type: str
    capabilities: List[str]

# Initialize Fusion components
telemetry_logger = AgentTelemetryLogger()
memory_manager = None  # Will be initialized per agent if needed

# Initialize dispatcher for proper agent routing
from core.dispatcher import dispatcher
from core.orchestrator import orchestrator

# Initialize agents dynamically from manifest and plugins
print("🚀 Loading agents dynamically...")
agent_map = load_agents()
print(f"✅ Loaded {len(agent_map)} core agents: {', '.join(agent_map.keys())}")

# Load plugins
plugin_agents = load_plugins()
agent_map.update(plugin_agents)
print(f"🔌 Total agents available: {len(agent_map)}")

# Initialize orchestrator
orchestrator = MultiAgentOrchestrator(
    agents=agent_map,
    evaluator_agent=agent_map.get("evaluator"),
    telemetry_logger=telemetry_logger,
    memory_manager=memory_manager
)

# Load agent manifest
def load_agent_manifest():
    try:
        with open("agent_manifest.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"agents": {}, "system_capabilities": {}}

agent_manifest = load_agent_manifest()

# Prompt Orchestrator Configuration
PROMPT_ORCHESTRATOR_URL = "http://localhost:8001"

async def call_prompt_orchestrator(prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call the prompt orchestrator service for prompt rewriting and analysis"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROMPT_ORCHESTRATOR_URL}/rewrite",
                json={
                    "prompt": prompt,
                    "context": context or {},
                    "use_memory": True,
                    "use_fallback": True
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Prompt orchestrator failed: {response.status_code}")
                return {"original_prompt": prompt, "rewritten_prompt": prompt, "confidence": 0.5}
                
    except Exception as e:
        print(f"⚠️ Prompt orchestrator error: {e}")
        return {"original_prompt": prompt, "rewritten_prompt": prompt, "confidence": 0.5}

async def get_agent_recommendation(prompt: str) -> Dict[str, Any]:
    """Get agent routing recommendation from prompt orchestrator"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{PROMPT_ORCHESTRATOR_URL}/route",
                json={
                    "prompt": prompt,
                    "confidence_threshold": 0.7
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"recommended_agent": "evaluator", "confidence": 0.5}
                
    except Exception as e:
        print(f"⚠️ Agent routing error: {e}")
        return {"recommended_agent": "evaluator", "confidence": 0.5}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Fusion v15 API",
        "version": "15.0.0",
        "endpoints": [
            "/prompt - Universal prompt handler with auto-agent selection",
            "/run - Run single agent",
            "/run_parallel - Run multiple agents", 
            "/agents - List available agents",
            "/status - System status",
            "/memory/{agent} - Get agent memory",
            "/telemetry - Get telemetry data"
        ]
    }

@app.post("/run")
async def run_agent(req: RunRequest):
    """Run a single agent with optional prompt orchestration"""
    if req.agent not in agent_map:
        raise HTTPException(status_code=404, detail=f"Agent '{req.agent}' not found")
    
    agent = agent_map[req.agent]
    
    # Initialize memory if requested
    memory = None
    if req.use_memory:
        memory = AgentMemory(req.agent)
    
    try:
        # Use prompt orchestrator if enabled
        final_input = req.input
        orchestrator_result = None
        
        if req.use_prompt_orchestrator:
            try:
                orchestrator_result = await call_prompt_orchestrator(req.input)
                if orchestrator_result.get("rewritten_prompt"):
                    final_input = orchestrator_result["rewritten_prompt"]
                    print(f"🔄 Prompt rewritten by orchestrator (confidence: {orchestrator_result.get('confidence', 0):.2f})")
            except Exception as e:
                print(f"⚠️ Prompt orchestrator failed, using original prompt: {e}")
        
        # Use dispatcher for proper agent execution
        output = await dispatcher.dispatch(req.agent, final_input)
        
        # Log to memory if enabled
        if memory:
            memory.append(req.input, output)
        
        # Log telemetry if enabled
        if req.use_telemetry:
            telemetry_logger.log_event(
                agent=req.agent,
                input_text=req.input,
                output_text=output
            )
        
        result = {
            "agent": req.agent,
            "output": output,
            "success": True,
            "memory_enabled": req.use_memory,
            "telemetry_enabled": req.use_telemetry,
            "prompt_orchestrator_used": req.use_prompt_orchestrator
        }
        
        # Include orchestrator metadata if used
        if orchestrator_result:
            result["orchestrator_metadata"] = {
                "original_prompt": orchestrator_result.get("original_prompt"),
                "rewritten_prompt": orchestrator_result.get("rewritten_prompt"),
                "pattern_type": orchestrator_result.get("pattern_type"),
                "confidence": orchestrator_result.get("confidence"),
                "suggested_agents": orchestrator_result.get("suggested_agents", [])
            }
        
        return result
        
    except Exception as e:
        # Log error
        if req.use_telemetry:
            telemetry_logger.log_event(
                agent=req.agent,
                input_text=req.input,
                output_text=f"Error: {str(e)}",
                fallback="error_handling"
            )
        
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.post("/run/auto")
async def run_auto(req: RunRequest):
    """
    Auto-routing endpoint that selects the best agent and rewrites prompts
    """
    try:
        # Step 1: Rewrite the prompt using orchestrator
        rewritten_prompt = await orchestrator.rewrite(req.input)
        
        # Step 2: Select the best agent for the rewritten prompt
        selected_agent = orchestrator.select_agent(rewritten_prompt)
        
        print(f"🎯 Auto-selected agent: {selected_agent} for prompt: {req.input[:50]}...")
        
        # Step 3: Dispatch to the selected agent
        output = await dispatcher.dispatch(selected_agent, rewritten_prompt)
        
        return {
            "agent": selected_agent,
            "input": req.input,
            "rewritten_prompt": rewritten_prompt,
            "output": output,
            "success": True,
            "auto_selected": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-routing failed: {str(e)}")

@app.post("/prompt") 
async def handle_prompt(req: PromptRequest):
    """
    Universal prompt handler with auto-agent selection
    Uses prompt orchestrator to determine best agent and rewrite prompt
    """
    try:
        # Get agent recommendation from prompt orchestrator
        agent_recommendation = None
        final_agent = req.agent_preference or "evaluator"
        
        if req.use_prompt_orchestrator:
            try:
                agent_recommendation = await get_agent_recommendation(req.input)
                recommended_agent = agent_recommendation.get("recommended_agent")
                
                # Use recommendation if agent exists and no preference specified
                if not req.agent_preference and recommended_agent in agent_map:
                    final_agent = recommended_agent
                    print(f"🎯 Auto-selected agent: {final_agent} (confidence: {agent_recommendation.get('confidence', 0):.2f})")
                    
            except Exception as e:
                print(f"⚠️ Agent recommendation failed: {e}")
        
        # Create RunRequest and execute
        run_request = RunRequest(
            agent=final_agent,
            input=req.input,
            use_memory=req.use_memory,
            use_telemetry=req.use_telemetry,
            use_prompt_orchestrator=req.use_prompt_orchestrator
        )
        
        result = await run_agent(run_request)
        
        # Add auto-selection metadata
        if agent_recommendation:
            result["auto_selection"] = {
                "recommended_agent": agent_recommendation.get("recommended_agent"),
                "confidence": agent_recommendation.get("confidence"),
                "alternatives": agent_recommendation.get("alternatives", []),
                "reasoning": agent_recommendation.get("reasoning")
            }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt handling failed: {str(e)}")

@app.post("/run_parallel")
async def run_parallel_agents(req: ParallelRunRequest):
    """Run multiple agents in parallel"""
    # Validate agents
    invalid_agents = [agent for agent in req.agents if agent not in agent_map]
    if invalid_agents:
        raise HTTPException(
            status_code=404, 
            detail=f"Agents not found: {invalid_agents}"
        )
    
    try:
        # Run parallel execution
        result = await orchestrator.run_parallel(req.input, req.agents)
        
        return {
            "input": req.input,
            "agents": req.agents,
            "top_result": result.get("top_result"),
            "all_results": result.get("all_results"),
            "evaluations": result.get("evaluations"),
            "execution_time": result.get("execution_time"),
            "agent_count": result.get("agent_count")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parallel execution failed: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List all available agents with their capabilities"""
    agents_info = {}
    
    for agent_name, agent in agent_map.items():
        manifest_info = agent_manifest.get("agents", {}).get(agent_name, {})
        
        agents_info[agent_name] = {
            "role": manifest_info.get("role", "Unknown"),
            "capabilities": manifest_info.get("capabilities", []),
            "confidence_threshold": manifest_info.get("confidence_threshold", 0.8),
            "memory_enabled": manifest_info.get("memory_enabled", True),
            "telemetry_enabled": manifest_info.get("telemetry_enabled", True),
            "type": type(agent).__name__,
            "available": True
        }
    
    return {
        "agents": agents_info,
        "total_agents": len(agent_map),
        "system_capabilities": agent_manifest.get("system_capabilities", {})
    }

@app.get("/status")
async def system_status():
    """Get system status and statistics"""
    # Get orchestrator status
    agent_status = orchestrator.get_agent_status()
    
    # Get telemetry stats
    telemetry_stats = telemetry_logger.get_session_stats()
    
    return {
        "system": {
            "version": "15.0.0",
            "status": "active",
            "agents_available": len(agent_map),
            "telemetry_enabled": True,
            "memory_enabled": True
        },
        "agents": agent_status,
        "telemetry": telemetry_stats,
        "manifest": {
            "version": agent_manifest.get("system_info", {}).get("version", "unknown"),
            "capabilities": agent_manifest.get("system_capabilities", {})
        }
    }

@app.get("/memory/{agent_name}")
async def get_agent_memory(agent_name: str, limit: int = 10):
    """Get memory for a specific agent"""
    if agent_name not in agent_map:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    try:
        memory = AgentMemory(agent_name)
        recent_memory = memory.get_last(limit)
        metadata = memory.get_metadata()
        
        return {
            "agent": agent_name,
            "recent_memory": recent_memory,
            "metadata": metadata,
            "memory_count": len(memory.data["history"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")

@app.get("/telemetry")
async def get_telemetry_data():
    """Get telemetry data for current session"""
    try:
        stats = telemetry_logger.get_session_stats()
        return {
            "session_id": telemetry_logger.session_id,
            "session_duration": stats.get("session_duration", 0),
            "total_events": stats.get("total_events", 0),
            "agent_usage": stats.get("agent_usage", {}),
            "fallback_rate": stats.get("fallback_rate", 0),
            "avg_confidence": stats.get("avg_confidence", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get telemetry: {str(e)}")

@app.post("/telemetry/export")
async def export_telemetry(format: str = "json"):
    """Export telemetry data"""
    try:
        if format == "json":
            data = telemetry_logger.save()
            return data
        elif format == "csv":
            csv_path = f"telemetry_export_{telemetry_logger.session_id}.csv"
            telemetry_logger.export_to_csv(csv_path)
            return {"message": f"Telemetry exported to {csv_path}"}
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.delete("/telemetry/clear")
async def clear_telemetry():
    """Clear current telemetry session"""
    try:
        telemetry_logger.clear_session()
        return {"message": "Telemetry session cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 