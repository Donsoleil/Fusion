# Fusion v15 - AI Agentic Operating System

## 🚀 Scalable ChatGPT-Style System

Fusion v15 has been completely refactored into a **scalable, microservice-based architecture** with a beautiful ChatGPT-style interface. This implementation follows the four-part scaling plan to transform Fusion from a CLI tool into a production-ready system.

## 🏗️ Architecture Overview

### Core Components

1. **Dynamic Agent Loader** (`core/agent_loader.py`)
   - Replaces static agent maps with manifest-driven loading
   - Supports plugin system for extending functionality

2. **Prompt Orchestrator Service** (`prompt_orchestrator.py`) 
   - Dedicated microservice for prompt analysis and rewriting
   - Runs on port 8001 with FastAPI
   - Provides `/rewrite`, `/route`, and `/analyze` endpoints

3. **Main API Service** (`fusion_api.py`)
   - Enhanced FastAPI service with prompt orchestration integration
   - Universal `/prompt` endpoint with auto-agent selection
   - Supports multipart uploads for voice and images

4. **Lightweight CLI** (`fusion_cli.py`)
   - HTTP-based CLI using Typer
   - Forwards all requests to the API layer
   - Supports voice and image attachments

5. **React Frontend** (`fusion_chat_frontend/`)
   - ChatGPT-style interface built with Next.js and shadcn/ui
   - Web Speech API for voice recording
   - Drag & drop image support
   - Real-time chat with all 32+ agents

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install fastapi uvicorn httpx typer[all] pydantic

# Install frontend dependencies
cd fusion_chat_frontend
npm install
```

### 2. Start the Services

**Terminal 1: Start Main API**
```bash
uvicorn fusion_api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Start Prompt Orchestrator**
```bash
python prompt_orchestrator.py
```

**Terminal 3: Start Frontend**
```bash
cd fusion_chat_frontend
npm run dev
```

### 3. Access the System

- **Web Interface**: http://localhost:3000
- **Main API**: http://localhost:8000
- **Prompt Orchestrator**: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs

## 💻 Usage Examples

### Web Interface
Open http://localhost:3000 for the ChatGPT-style interface with:
- ✅ Text prompts with auto-agent selection
- ✅ Voice recording (Web Speech API)
- ✅ Image drag & drop
- ✅ Real-time chat bubbles
- ✅ Agent metadata display
- ✅ Prompt orchestrator toggle

### CLI Usage
```bash
# Simple prompt (auto-selects best agent)
./fusion_cli.py prompt "Design a mobile app for Bitcoin trading"

# Specific agent
./fusion_cli.py prompt "Critique this design" --agent evaluator

# With voice and images
./fusion_cli.py prompt "Analyze this content" --voice memo.wav --images ui.png,wireframe.png

# List available agents
./fusion_cli.py agents

# Check system status
./fusion_cli.py status
```

### API Usage
```bash
# Universal prompt endpoint (recommended)
curl -X POST "http://localhost:8000/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Design a mobile app interface",
    "use_prompt_orchestrator": true
  }'

# Direct agent execution
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "vp_design",
    "input": "Design a mobile app interface",
    "use_prompt_orchestrator": true
  }'
```

## 🔧 Available Agents

Fusion v15 includes 32+ specialized AI agents:

### Core Agents
- `vp_design` - Design leadership and strategy
- `evaluator` - Quality assessment and scoring  
- `creative_director` - Creative direction and vision
- `design_technologist` - Technical design implementation

### Strategic Agents  
- `strategy_pilot` - Strategic planning and execution
- `vp_of_product` - Product strategy and roadmaps
- `market_analyst` - Market research and analysis
- `product_navigator` - Product navigation and UX

### Content & Communication
- `content_designer` - Content strategy and copy
- `deck_narrator` - Presentation and storytelling
- `portfolio_editor` - Portfolio curation
- `research_summarizer` - Research synthesis

### And 20+ more specialized agents...

## 🔌 Plugin System

### Adding Custom Agents

1. Create a plugin file in `plugins/my_custom_agent.py`:

```python
class MyCustomAgent:
    def __init__(self):
        self.name = "my_custom_agent"
    
    async def run(self, input_text: str) -> str:
        return f"Custom agent processed: {input_text}"

# Optional configuration
PLUGIN_CONFIG = {
    "agent_settings": {
        "confidence_threshold": 0.8,
        "max_retries": 3
    }
}
```

2. Restart the services - plugins are auto-discovered!

## 📊 System Features

### Scalability Features
- ✅ **Single source of truth** for agent registration (manifest-driven)
- ✅ **Plugin registry** for easy extensibility  
- ✅ **Dedicated prompt orchestrator** for high-precision rewriting
- ✅ **API-first architecture** ready for auth, rate limits, multi-tenancy

### Next-Generation Capabilities
- ✅ **Conversational threads** with persistent memory
- ✅ **Agent metadata** and confidence scoring
- ✅ **Pattern-based routing** with fallback handling
- ✅ **Real-time telemetry** and performance monitoring
- ✅ **Multimodal support** (text, voice, images)

### Production-Ready
- ✅ **Microservice architecture** for independent scaling
- ✅ **Health checks** and monitoring endpoints
- ✅ **Error handling** with graceful fallbacks
- ✅ **TypeScript frontend** with modern React patterns
- ✅ **Responsive design** with dark mode support

## 🛣️ Roadmap v16.0

### Visual Workflow Builder
- Drag-and-drop agent orchestration
- Visual pattern designer
- Real-time workflow execution

### Advanced Features
- **Agent Bundles**: Curated sets by domain (design, strategy, market)
- **Embeddable Widget**: Drop Fusion into any web page
- **Multi-tenant Support**: Per-customer agent customization
- **Advanced Analytics**: Usage patterns and optimization insights

### Enterprise Features
- **SSO Integration**: SAML, OAuth, Active Directory
- **Rate Limiting**: Per-user and per-agent quotas
- **Audit Logging**: Complete conversation history
- **White-label Support**: Custom branding and domains

## 📁 Project Structure

```
fusion_v13/
├── core/
│   └── agent_loader.py          # Dynamic agent loading
├── agents/                      # All 32+ agent implementations
├── fusion_api.py               # Main FastAPI service  
├── prompt_orchestrator.py      # Prompt enhancement service
├── fusion_cli.py               # Lightweight HTTP CLI
├── fusion_chat_frontend/        # React frontend
│   ├── src/components/
│   │   ├── FusionChat.tsx      # Main chat component
│   │   └── ui/                 # shadcn/ui components
│   └── package.json
├── plugins/                    # Plugin directory
├── memory/                     # Persistent agent memory
└── README.md                   # This file
```

## 🔧 Development

### Adding New Agents
1. Create `agents/new_agent_agent.py` 
2. Add entry to `agent_manifest.json`
3. Restart services - auto-loaded!

### Frontend Development
```bash
cd fusion_chat_frontend
npm run dev          # Development server
npm run build        # Production build
npm run start        # Production server
```

### API Development
```bash
uvicorn fusion_api:app --reload --host 0.0.0.0 --port 8000
# Auto-reloads on code changes
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your agent/feature to the appropriate directory
4. Test with both CLI and web interface
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

---

**Fusion v15** - From CLI to ChatGPT-style scalable system in one transformative update. 🚀