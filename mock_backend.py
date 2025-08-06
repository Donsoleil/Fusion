print("🚀 Mock Fusion API running on http://localhost:8000")
import http.server
import socketserver
import json

class MockHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/prompt":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            mock_response = {
                "agent": "vp_design",
                "output": "🎯 Hello from Fusion v15! This is a mock response from the VP Design agent. Your beautiful ChatGPT-style interface is working perfectly! The backend services will be fully functional once we resolve the Python package installation.",
                "success": True,
                "prompt_orchestrator_used": True
            }
            self.wfile.write(json.dumps(mock_response).encode())
        else:
            super().do_POST()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

PORT = 8000
with socketserver.TCPServer(("", PORT), MockHandler) as httpd:
    print(f"Mock API server running on port {PORT}")
    httpd.serve_forever()
