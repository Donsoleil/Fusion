#!/usr/bin/env python3
"""
Dynamic Agent Loader for Fusion v15
Replaces static agent maps with manifest-driven dynamic loading
"""

import json
import importlib
import os
from typing import Dict, Any, Type, Optional
from pathlib import Path


class AgentLoader:
    """Dynamic agent loader that reads from agent_manifest.json"""
    
    def __init__(self, manifest_path: str = "agent_manifest.json", plugins_dir: str = "plugins"):
        self.manifest_path = manifest_path
        self.plugins_dir = Path(plugins_dir)
        self.loaded_agents = {}
        self.manifest_data = {}
        
    def load_agents(self) -> Dict[str, Any]:
        """
        Load all agents from manifest and plugins directory.
        
        Returns:
            Dictionary mapping agent names to agent instances
        """
        agents = {}
        
        # Load core agents from manifest
        core_agents = self._load_core_agents()
        agents.update(core_agents)
        
        # Load plugin agents
        plugin_agents = self._load_plugin_agents()
        agents.update(plugin_agents)
        
        self.loaded_agents = agents
        return agents
    
    def _load_core_agents(self) -> Dict[str, Any]:
        """Load agents defined in the manifest file"""
        agents = {}
        
        try:
            with open(self.manifest_path, 'r') as f:
                self.manifest_data = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Warning: Manifest file {self.manifest_path} not found")
            return agents
        
        manifest_agents = self.manifest_data.get("agents", {})
        
        for agent_name, agent_config in manifest_agents.items():
            try:
                # Convert agent name to module and class name
                module_name = f"agents.{agent_name}_agent"
                class_name = self._snake_to_pascal(agent_name) + "Agent"
                
                # Import and instantiate the agent
                module = importlib.import_module(module_name)
                agent_class = getattr(module, class_name)
                agent_instance = agent_class()
                
                agents[agent_name] = agent_instance
                print(f"✅ Loaded agent: {agent_name}")
                
            except (ImportError, AttributeError) as e:
                print(f"⚠️ Failed to load agent {agent_name}: {e}")
                continue
        
        return agents
    
    def _load_plugin_agents(self) -> Dict[str, Any]:
        """Load agents from plugins directory"""
        from fusion_plugin_registry import plugin_registry
        
        agents = {}
        
        if not self.plugins_dir.exists():
            print(f"🔌 Creating plugins directory: {self.plugins_dir}")
            self.plugins_dir.mkdir(exist_ok=True)
            return agents
        
        # Discover and register plugins
        discovery_results = plugin_registry.discover_plugins()
        
        # Get registered plugin agents
        for agent_name in plugin_registry.list_agents():
            try:
                agent_class = plugin_registry.get_agent(agent_name)
                agent_instance = agent_class()
                agents[agent_name] = agent_instance
                print(f"🔌 Loaded plugin agent: {agent_name}")
            except Exception as e:
                print(f"⚠️ Failed to instantiate plugin agent {agent_name}: {e}")
        
        if discovery_results["agents_found"] > 0:
            print(f"🔌 Plugin discovery summary: {discovery_results['agents_found']} agents, {discovery_results['tools_found']} tools")
        
        return agents
    
    def _snake_to_pascal(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        return "".join(word.capitalize() for word in snake_str.split("_"))
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent"""
        return self.manifest_data.get("agents", {}).get(agent_name)
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get system capabilities from manifest"""
        return self.manifest_data.get("system_capabilities", {})
    
    def list_available_agents(self) -> Dict[str, Any]:
        """List all available agents with their metadata"""
        agents_info = {}
        
        for agent_name, agent_instance in self.loaded_agents.items():
            config = self.get_agent_config(agent_name) or {}
            
            agents_info[agent_name] = {
                "role": config.get("role", "Unknown"),
                "capabilities": config.get("capabilities", []),
                "confidence_threshold": config.get("confidence_threshold", 0.8),
                "memory_enabled": config.get("memory_enabled", True),
                "telemetry_enabled": config.get("telemetry_enabled", True),
                "type": type(agent_instance).__name__,
                "available": True
            }
        
        return agents_info


# Global instance for easy access
agent_loader = AgentLoader()


def load_agents(manifest_path: str = "agent_manifest.json") -> Dict[str, Any]:
    """
    Load agents from manifest file.
    
    Args:
        manifest_path: Path to agent manifest file
        
    Returns:
        Dictionary mapping agent names to agent instances
    """
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        
        agents = {}
        for name in data["agents"]:
            try:
                module = importlib.import_module(f"agents.{name}_agent")
                cls_name = "".join([w.title() for w in name.split("_")]) + "Agent"
                cls = getattr(module, cls_name)
                agents[name] = cls()
                print(f"✅ Loaded agent: {name}")
            except (ImportError, AttributeError) as e:
                print(f"⚠️ Failed to load agent {name}: {e}")
                continue
        
        return agents
    except FileNotFoundError:
        print(f"⚠️ Warning: Manifest file {manifest_path} not found")
        return {}

def load_plugins(plugins_dir: str = "plugins") -> Dict[str, Any]:
    """
    Load and register plugins from plugins directory.
    
    Args:
        plugins_dir: Directory containing plugin files
        
    Returns:
        Dictionary mapping plugin agent names to instances
    """
    import os
    from fusion_plugin_registry import plugin_registry
    
    plugin_agents = {}
    
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir, exist_ok=True)
        return plugin_agents
    
    # Discover and register plugins
    discovery_results = plugin_registry.discover_plugins()
    
    # Get registered plugin agents
    for agent_name in plugin_registry.list_agents():
        try:
            agent_class = plugin_registry.get_agent(agent_name)
            agent_instance = agent_class()
            plugin_agents[agent_name] = agent_instance
            print(f"🔌 Loaded plugin agent: {agent_name}")
        except Exception as e:
            print(f"⚠️ Failed to instantiate plugin agent {agent_name}: {e}")
    
    if discovery_results["agents_found"] > 0:
        print(f"🔌 Plugin discovery: {discovery_results['agents_found']} agents, {discovery_results['tools_found']} tools")
    
    return plugin_agents

def load_all_agents(manifest_path: str = "agent_manifest.json", plugins_dir: str = "plugins") -> Dict[str, Any]:
    """
    Load both core agents and plugins.
    
    Args:
        manifest_path: Path to agent manifest file
        plugins_dir: Directory containing plugin agents
        
    Returns:
        Dictionary mapping all agent names to agent instances
    """
    # Load core agents
    agents = load_agents(manifest_path)
    
    # Load plugin agents
    plugin_agents = load_plugins(plugins_dir)
    
    # Merge plugin agents
    agents.update(plugin_agents)
    
    return agents


# Example usage
if __name__ == "__main__":
    print("🚀 Testing Dynamic Agent Loader")
    
    # Load all agents
    agents = load_agents()
    
    print(f"\n📊 Summary:")
    print(f"Total agents loaded: {len(agents)}")
    print(f"Available agents: {', '.join(agents.keys())}")
    
    # Test agent info
    agent_info = agent_loader.list_available_agents()
    print(f"\n📋 Agent Details:")
    for name, info in agent_info.items():
        print(f"  {name}: {info['role']} ({len(info['capabilities'])} capabilities)")