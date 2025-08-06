#!/usr/bin/env python3
"""
Fusion CLI v15 - Lightweight HTTP API Client
Simple CLI that forwards all requests to the Fusion HTTP API
"""

import typer
import httpx
import json
import sys
from pathlib import Path
from typing import Optional, List
import asyncio

app = typer.Typer(
    name="fusion",
    help="Fusion v15 - AI Agentic Operating System CLI",
    no_args_is_help=True
)

# Configuration
FUSION_API_URL = "http://localhost:8000"
PROMPT_ORCHESTRATOR_URL = "http://localhost:8001"

def print_status(message: str, emoji: str = "🚀"):
    """Print formatted status message"""
    typer.echo(f"{emoji} {message}")

def print_error(message: str):
    """Print formatted error message"""
    typer.echo(f"❌ Error: {message}", err=True)

def print_success(message: str):
    """Print formatted success message"""
    typer.echo(f"✅ {message}")

async def check_api_health():
    """Check if Fusion API is running"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{FUSION_API_URL}/")
            return response.status_code == 200
    except:
        return False

async def check_orchestrator_health():
    """Check if Prompt Orchestrator is running"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{PROMPT_ORCHESTRATOR_URL}/health")
            return response.status_code == 200
    except:
        return False

def read_file_safely(file_path: str) -> Optional[str]:
    """Safely read file content"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print_error(f"Could not read file {file_path}: {e}")
        return None

@app.command()
def prompt(
    text: str = typer.Argument(..., help="Your prompt text"),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Specific agent to use"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice file path (.wav)"),
    images: Optional[str] = typer.Option(None, "--images", help="Comma-separated image file paths"),
    memory: bool = typer.Option(True, "--memory/--no-memory", help="Use agent memory"),
    telemetry: bool = typer.Option(True, "--telemetry/--no-telemetry", help="Enable telemetry"),
    orchestrator: bool = typer.Option(True, "--orchestrator/--no-orchestrator", help="Use prompt orchestrator"),
    raw: bool = typer.Option(False, "--raw", help="Output raw JSON response"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Send a prompt to Fusion with optional voice and image attachments
    
    Examples:
        fusion prompt "Design a mobile app for Bitcoin trading"
        fusion prompt "Critique this design" --agent evaluator
        fusion prompt "Review this interface" --images ui.png,wireframe.png
        fusion prompt "Analyze this voice memo" --voice memo.wav
    """
    asyncio.run(_handle_prompt(text, agent, voice, images, memory, telemetry, orchestrator, raw, verbose))

async def _handle_prompt(text: str, agent: Optional[str], voice: Optional[str], 
                        images: Optional[str], memory: bool, telemetry: bool, 
                        orchestrator: bool, raw: bool, verbose: bool):
    """Handle prompt command asynchronously"""
    
    if verbose:
        print_status("Checking Fusion API status...")
    
    # Check API health
    api_healthy = await check_api_health()
    if not api_healthy:
        print_error("Fusion API is not running. Please start it with: uvicorn fusion_api:app --reload")
        sys.exit(1)
    
    # Check orchestrator health if needed
    if orchestrator:
        orchestrator_healthy = await check_orchestrator_health()
        if not orchestrator_healthy:
            print_error("Prompt Orchestrator is not running. Starting in no-orchestrator mode...")
            orchestrator = False
    
    # Prepare request data
    request_data = {
        "input": text,
        "use_memory": memory,
        "use_telemetry": telemetry,
        "use_prompt_orchestrator": orchestrator
    }
    
    if agent:
        request_data["agent_preference"] = agent
    
    # Handle file attachments (placeholder for multipart support)
    if voice:
        voice_content = read_file_safely(voice)
        if voice_content:
            request_data["voice_attachment"] = voice
            if verbose:
                print_status(f"Attached voice file: {voice}")
    
    if images:
        image_list = [img.strip() for img in images.split(",")]
        valid_images = []
        for img in image_list:
            if Path(img).exists():
                valid_images.append(img)
                if verbose:
                    print_status(f"Attached image: {img}")
            else:
                print_error(f"Image file not found: {img}")
        
        if valid_images:
            request_data["image_attachments"] = valid_images
    
    if verbose:
        print_status(f"Sending prompt to {'specific agent: ' + agent if agent else 'auto-selected agent'}")
        if orchestrator:
            print_status("Using prompt orchestrator for enhancement")
    
    # Send request to Fusion API
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            endpoint = "/prompt"  # Universal prompt endpoint
            response = await client.post(f"{FUSION_API_URL}{endpoint}", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if raw:
                    # Output raw JSON
                    print(json.dumps(result, indent=2))
                else:
                    # Formatted output
                    print_success("Fusion Response:")
                    print()
                    
                    # Show agent selection info
                    if "auto_selection" in result:
                        auto_info = result["auto_selection"]
                        print(f"🎯 Agent: {result['agent']} (auto-selected, confidence: {auto_info.get('confidence', 0):.2f})")
                        if verbose and auto_info.get("reasoning"):
                            print(f"💭 Reasoning: {auto_info['reasoning']}")
                    else:
                        print(f"🎯 Agent: {result['agent']}")
                    
                    # Show orchestrator info if used
                    if "orchestrator_metadata" in result and verbose:
                        meta = result["orchestrator_metadata"]
                        print(f"🔄 Orchestrator: {meta.get('pattern_type', 'unknown')} pattern (confidence: {meta.get('confidence', 0):.2f})")
                    
                    print()
                    print("📄 Output:")
                    print("-" * 60)
                    print(result["output"])
                    print("-" * 60)
                    
                    if verbose:
                        print()
                        print(f"⚡ Memory: {'enabled' if result.get('memory_enabled') else 'disabled'}")
                        print(f"📊 Telemetry: {'enabled' if result.get('telemetry_enabled') else 'disabled'}")
                        print(f"🔄 Orchestrator: {'used' if result.get('prompt_orchestrator_used') else 'bypassed'}")
            else:
                print_error(f"API request failed with status {response.status_code}")
                if verbose:
                    print(f"Response: {response.text}")
                sys.exit(1)
                
    except httpx.TimeoutException:
        print_error("Request timed out. The agent might be processing a complex request.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Request failed: {e}")
        sys.exit(1)

@app.command()
def agents():
    """List all available agents"""
    asyncio.run(_list_agents())

async def _list_agents():
    """List available agents asynchronously"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{FUSION_API_URL}/agents")
            
            if response.status_code == 200:
                data = response.json()
                agents_info = data.get("agents", {})
                
                print_success(f"Available Agents ({data.get('total_agents', 0)}):")
                print()
                
                for agent_name, info in agents_info.items():
                    status = "🟢" if info.get("available") else "🔴"
                    role = info.get("role", "Unknown")
                    capabilities = len(info.get("capabilities", []))
                    
                    print(f"{status} {agent_name}")
                    print(f"   Role: {role}")
                    print(f"   Capabilities: {capabilities}")
                    print()
                    
            else:
                print_error(f"Failed to get agents: {response.status_code}")
                
    except Exception as e:
        print_error(f"Failed to get agents: {e}")

@app.command()
def status():
    """Check system status"""
    asyncio.run(_check_status())

async def _check_status():
    """Check system status asynchronously"""
    print_status("Checking Fusion system status...")
    
    # Check main API
    api_healthy = await check_api_health()
    api_status = "🟢 Running" if api_healthy else "🔴 Not running"
    print(f"Fusion API: {api_status}")
    
    # Check orchestrator
    orchestrator_healthy = await check_orchestrator_health()
    orchestrator_status = "🟢 Running" if orchestrator_healthy else "🔴 Not running"
    print(f"Prompt Orchestrator: {orchestrator_status}")
    
    # Get detailed status if API is running
    if api_healthy:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{FUSION_API_URL}/status")
                
                if response.status_code == 200:
                    data = response.json()
                    system_info = data.get("system", {})
                    agents_info = data.get("agents", {})
                    
                    print()
                    print_success("System Details:")
                    print(f"Version: {system_info.get('version', 'unknown')}")
                    print(f"Agents Available: {system_info.get('agents_available', 0)}")
                    print(f"Memory Enabled: {system_info.get('memory_enabled', False)}")
                    print(f"Telemetry Enabled: {system_info.get('telemetry_enabled', False)}")
                    
        except Exception as e:
            print_error(f"Could not get detailed status: {e}")

@app.command() 
def run(
    agent: str = typer.Argument(..., help="Agent name to run"),
    text: str = typer.Argument(..., help="Input text for the agent"),
    memory: bool = typer.Option(True, "--memory/--no-memory", help="Use agent memory"),
    telemetry: bool = typer.Option(True, "--telemetry/--no-telemetry", help="Enable telemetry"),
    orchestrator: bool = typer.Option(False, "--orchestrator/--no-orchestrator", help="Use prompt orchestrator"),
    raw: bool = typer.Option(False, "--raw", help="Output raw JSON response")
):
    """
    Run a specific agent directly (legacy compatibility)
    
    Examples:
        fusion run vp_design "Design a mobile app interface"
        fusion run evaluator "Critique this design approach" --orchestrator
    """
    asyncio.run(_run_agent(agent, text, memory, telemetry, orchestrator, raw))

async def _run_agent(agent: str, text: str, memory: bool, telemetry: bool, orchestrator: bool, raw: bool):
    """Run specific agent asynchronously"""
    
    request_data = {
        "agent": agent,
        "input": text,
        "use_memory": memory,
        "use_telemetry": telemetry,
        "use_prompt_orchestrator": orchestrator
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{FUSION_API_URL}/run", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if raw:
                    print(json.dumps(result, indent=2))
                else:
                    print_success(f"Agent '{agent}' Response:")
                    print()
                    print(result["output"])
                    
            else:
                print_error(f"Agent execution failed: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print_error(f"Agent execution failed: {e}")

if __name__ == "__main__":
    app()