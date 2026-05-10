# LiveKit Calendar Voice Agent

A production-ready voice assistant built with LiveKit and LangGraph that manages your Google Calendar. It supports natural voice interactions, handles appointments (search, create, update, cancel), and features a robust multi-model LLM fallback system.

## Features

- **Voice Interface:** High-quality STT and TTS using Sarvam AI.
- **Calendar Integration:** Full management of Google Calendar events.
- **Intelligent Routing:** Powered by LangGraph with a dynamic "Acknowledgement" system for low-latency feedback.
- **Resilient LLM Chain:** Primary reasoning via Groq (Llama 3.3 70B) with automatic fallbacks to Llama 3.1 8B and Gemini 2.0 Flash Lite.
- **Production Observability:** Integrated with LangSmith for comprehensive tracing and monitoring.
- **Natural Conversations:** Features turn detection tuning and background ambient noise for a premium feel.

## Prerequisites

- Python 3.10+
- [LiveKit Cloud](https://livekit.io/cloud) project
- API Keys for:
  - LiveKit (URL, API Key, Secret)
  - Sarvam AI
  - Groq
  - Google Cloud (for Calendar API)
  - LangSmith (optional, for tracing)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/PrabhudattaPatra/livekit_agent.git
   cd livekit_agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file:
   ```env
   LIVEKIT_URL=<your-livekit-url>
   LIVEKIT_API_KEY=<your-api-key>
   LIVEKIT_API_SECRET=<your-api-secret>
   SARVAM_API_KEY=<your-sarvam-key>
   GROQ_API_KEY=<your-groq-key>
   GOOGLE_API_KEY=<your-google-key>
   OTEL_EXPORTER_OTLP_ENDPOINT="https://api.smith.langchain.com/otel"
   OTEL_EXPORTER_OTLP_HEADERS="x-api-key=<your-langsmith-key>"
   ```

4. Authenticate with Google:
   Ensure your `credentials.json` is present and run your authentication script to generate `token.json`.

## Usage

Start the agent:
```bash
python agent.py dev
```

The agent will connect to your LiveKit project. You can then join the room via the LiveKit sandbox or a custom frontend to start interacting with your calendar.

## Project Structure

- `agent.py`: Entry point, LiveKit session management, and agent orchestration.
- `langgraph_agent.py`: LangGraph logic, calendar tool definitions, and LLM fallback configuration.
- `langsmith_processor.py`: Custom telemetry processor for LangSmith integration.
- `requirements.txt`: Project dependencies.

## License

[MIT](LICENSE)
