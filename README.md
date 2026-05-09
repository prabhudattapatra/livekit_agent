# LiveKit Voice AI Assistant

A production-ready, ultra-low latency voice AI assistant built with LiveKit, FastAPI, and LangGraph. The assistant acts as a receptionist that can schedule, modify, and cancel appointments using Google Calendar.

## Architecture

This project uses a decoupled, event-driven architecture to ensure scalability and fault tolerance:

1. **FastAPI Backend (`server.py`)**: A lightweight web server that securely generates LiveKit access tokens and serves the static frontend UI.
2. **LiveKit Agent Worker (`agent.py`)**: A persistent background worker that connects to LiveKit WebRTC rooms. It handles speech-to-text (STT), text-to-speech (TTS), and voice activity detection (VAD).
3. **LangGraph Logic (`langgraph_agent.py`)**: The cognitive engine of the assistant. It uses Groq's lightning-fast `llama-3.3-70b-versatile` model alongside LangChain's Google Calendar tools to execute complex user requests.
4. **Glassmorphic Frontend (`static/`)**: A sleek, pure Vanilla JS/CSS frontend that establishes peer-to-peer WebRTC connections with the agent and displays real-time state animations (Listening, Thinking, Speaking).

## Technology Stack
- **WebRTC/Voice**: LiveKit Server & `livekit-agents`
- **STT/TTS**: Sarvam AI (`saaras:v3` / `bulbul:v3`)
- **LLM/Orchestration**: Groq, LangChain, LangGraph
- **Backend API**: FastAPI, Uvicorn
- **Integrations**: Google Calendar API

## Setup & Installation

### 1. Prerequisites
- Python 3.10+
- `uv` (Fast Python package installer)
- LiveKit Cloud account (or local LiveKit Server)
- Groq API Key
- Sarvam API Key
- Google Cloud Service Account with Calendar API enabled

### 2. Environment Variables
Create a `.env` file in the root directory and add the following keys:
```env
LIVEKIT_URL=wss://<your-project>.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

GROQ_API_KEY=your_groq_key
SARVAM_API_KEY=your_sarvam_key

# Optional LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
```

### 3. Google Calendar Credentials
Place your Google OAuth credentials in the root directory:
- `credentials.json`
- `token.json` 

*(Note: These files are included in `.gitignore` by default to prevent accidental security leaks).*

### 4. Install Dependencies
```bash
uv pip install -r requirement.txt
```

## Running the Application

Because this is a decoupled architecture, you must run the Web Server and the Agent Worker in two separate terminals.

**Terminal 1: Start the Voice Agent Worker**
```bash
uv run python agent.py dev
```

**Terminal 2: Start the FastAPI Backend**
```bash
uv run uvicorn server:app
```

Once both are running, open your browser and navigate to:
[http://localhost:8000](http://localhost:8000)

Click **"Connect to Agent"** and start speaking!

## Capabilities
- **Book Appointments**: Checks real-time availability and schedules 60-minute blocks.
- **Update Appointments**: Locates appointments by email and modifies times/titles dynamically.
- **Cancel Appointments**: Confirms specific meeting details before safely deleting them.
- **Dynamic Fallbacks**: Gracefully handles API rate limits by falling back to Gemini 2.0.

## Production Deployment (Render)

This project includes a `render.yaml` Blueprint file for seamless 1-click deployments to [Render](https://render.com). 
It automatically deploys both the Web Server and the Background Worker as two separate, highly available services.

### How to Deploy:
1. Fork or push this repository to your GitHub account.
2. Sign in to Render, go to **Blueprints**, and select **New Blueprint Instance**.
3. Connect your repository.
4. Render will detect the two services. Before deploying, you will be prompted to enter your Environment Variables.
5. **Handling Google Secrets in the Cloud**: 
   Since `credentials.json` and `token.json` are blocked from GitHub for your security, you must copy their contents and paste them as strings into the `GOOGLE_CRED_JSON` and `GOOGLE_TOKEN_JSON` environment variables in the Render dashboard. 
   *(The `init_secrets.py` script will automatically recreate the JSON files securely when the server boots).*
