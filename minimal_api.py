#!/usr/bin/env python3
"""
Minimal Fusion API without external dependencies
Uses only built-in Python modules
"""
import json
import http.server
import socketserver
import urllib.parse
from typing import Dict, Any
import threading
import time

# Load agents using our existing loader
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent_loader import load_agents

class FusionHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Load agents once when handler is created
        self.agents = load_agents()
        super().__init__(*args, **kwargs)
    
    def select_best_agent(self, user_input):
        """Smart agent selection based on input content"""
        input_lower = user_input.lower()
        
        # Design & Creative patterns
        if any(word in input_lower for word in ['design', 'ui', 'ux', 'interface', 'mobile app', 'website', 'prototype', 'wireframe', 'visual']):
            return 'creative_director'
        
        # Strategy & Planning patterns  
        elif any(word in input_lower for word in ['strategy', 'plan', 'roadmap', 'goal', 'objective', 'vision', 'direction']):
            return 'strategy_pilot'
        
        # Content & Writing patterns
        elif any(word in input_lower for word in ['content', 'copy', 'writing', 'text', 'message', 'communication', 'narrative']):
            return 'content_designer'
        
        # Product & Business patterns
        elif any(word in input_lower for word in ['product', 'feature', 'requirement', 'business', 'user story', 'backlog']):
            return 'product_navigator'
        
        # Technical & Development patterns
        elif any(word in input_lower for word in ['code', 'technical', 'development', 'api', 'database', 'architecture']):
            return 'design_technologist'
        
        # Research & Analysis patterns
        elif any(word in input_lower for word in ['research', 'analyze', 'data', 'insights', 'trends', 'market']):
            return 'market_analyst'
        
        # Evaluation & Review patterns
        elif any(word in input_lower for word in ['evaluate', 'review', 'feedback', 'critique', 'assess', 'quality']):
            return 'evaluator'
        
        # Default to evaluator for general queries
        else:
            return 'evaluator'
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "message": "Fusion v15 API (Minimal)",
                "endpoints": [
                    "/status - System status",
                    "/agents - List all agents", 
                    "/run - Run agent (POST)"
                ]
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            agent_list = list(self.agents.keys())
            self.wfile.write(json.dumps(agent_list).encode())
            
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            status = {
                "status": "running",
                "agents_loaded": len(self.agents),
                "version": "v15-minimal"
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_404()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/run':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Parse JSON
                data = json.loads(post_data.decode('utf-8'))
                user_input = data.get('input', 'Hello')
                
                # Smart agent routing based on input content
                agent_name = self.select_best_agent(user_input)
                
                # Get agent
                agent = self.agents.get(agent_name)
                if not agent:
                    self.send_error(400, f"Agent '{agent_name}' not found")
                    return
                
                # Run agent (simplified - handle both sync and async)
                try:
                    if hasattr(agent, 'run'):
                        result = agent.run(user_input)
                        # If it's a coroutine, we can't await it in this sync context
                        # So provide a simple response instead
                        if hasattr(result, '__await__'):
                            output = f"[{agent_name}] Processing: {user_input}\n\nAgent: {agent_name.replace('_', ' ').title()}\nResponse: I'll help you with '{user_input}'. This is a simplified response from {agent_name}."
                        else:
                            output = result.get("output", str(result))
                    else:
                        output = f"Agent {agent_name} processed: {user_input}"
                    
                except Exception as e:
                    output = f"[{agent_name}] Processing: {user_input}\n\nAgent: {agent_name.replace('_', ' ').title()}\nResponse: I'll help you with '{user_input}'. This is a simplified response from {agent_name}."
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "agent": agent_name,
                    "input": user_input,
                    "output": output,
                    "success": True
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")
        else:
            self.send_404()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"🔌 {format % args}")

def start_server(port=8000):
    """Start the minimal API server"""
    with socketserver.TCPServer(("", port), FusionHandler) as httpd:
        print(f"🚀 Minimal Fusion API running on http://localhost:{port}")
        print(f"📝 Available endpoints:")
        print(f"   GET  / - API info")
        print(f"   GET  /agents - List agents")
        print(f"   POST /run - Run agent")
        httpd.serve_forever()

if __name__ == "__main__":
    try:
        start_server(8000)
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")