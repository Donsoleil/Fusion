#!/bin/bash

# Fusion v15 System Launcher
# Starts all services for the complete ChatGPT-style system

echo "🚀 Starting Fusion v15 - AI Agentic Operating System"
echo "======================================================"

# Check if dependencies are installed
echo "📦 Checking dependencies..."

# Check Python dependencies
if ! python3 -c "import fastapi, uvicorn, httpx, typer" 2>/dev/null; then
    echo "❌ Missing Python dependencies. Installing..."
    pip3 install fastapi uvicorn httpx "typer[all]" pydantic --user
fi

# Check if frontend dependencies are installed
if [ ! -d "fusion_chat_frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd fusion_chat_frontend
    npm install
    cd ..
fi

echo "✅ Dependencies ready"

# Create necessary directories
mkdir -p plugins memory

echo ""
echo "🔧 Starting services..."
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down Fusion v15..."
    kill $API_PID $ORCHESTRATOR_PID $FRONTEND_PID 2>/dev/null
    wait
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start Prompt Orchestrator (port 8001)
echo "🧠 Starting Prompt Orchestrator..."
python3 prompt_orchestrator.py &
ORCHESTRATOR_PID=$!

# Wait a moment for orchestrator to start
sleep 2

# Start Main API (port 8000)
echo "🔌 Starting Fusion API..."
python3 -m uvicorn fusion_api:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start Frontend (port 3000)
echo "🎨 Starting React Frontend..."
cd fusion_chat_frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for services to initialize
echo ""
echo "⏳ Initializing services..."
sleep 5

echo ""
echo "✅ Fusion v15 is now running!"
echo "=============================="
echo ""
echo "🌐 Web Interface:      http://localhost:3000"
echo "🔌 Main API:           http://localhost:8000"
echo "🧠 Prompt Orchestrator: http://localhost:8001"
echo "📚 API Documentation:   http://localhost:8000/docs"
echo ""
echo "💡 Usage Examples:"
echo "   Web: Open http://localhost:3000 for ChatGPT-style interface"
echo "   CLI: ./fusion_cli.py prompt \"Design a mobile app\""
echo "   API: curl -X POST http://localhost:8000/prompt -H \"Content-Type: application/json\" -d '{\"input\":\"Hello Fusion\"}'"
echo ""
echo "🔍 Available Agents:"
echo "   • vp_design - Design leadership"
echo "   • evaluator - Quality assessment"  
echo "   • creative_director - Creative vision"
echo "   • strategy_pilot - Strategic planning"
echo "   • And 28+ more agents..."
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait