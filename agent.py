import asyncio
import logging
import uuid
import os
import json

from dotenv import load_dotenv
load_dotenv()

def _setup_google_secrets():
    # Cloud environments inject secrets via Env Vars since files aren't committed
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    token_json = os.getenv("GOOGLE_TOKEN_JSON")

    if creds_json and not os.path.exists("credentials.json"):
        with open("credentials.json", "w") as f:
            f.write(creds_json)
    
    if token_json and not os.path.exists("token.json"):
        with open("token.json", "w") as f:
            f.write(token_json)

_setup_google_secrets()
from livekit.agents.beta.tools import EndCallTool
from opentelemetry.sdk.trace import TracerProvider
from livekit.agents.telemetry import set_tracer_provider
from langsmith_processor import LangSmithSpanProcessor

def setup_langsmith():
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    if not endpoint or not headers:
        print("⚠️  Warning: OTEL environment variables not set. Tracing disabled.")
        return
    trace_provider = TracerProvider()
    trace_provider.add_span_processor(LangSmithSpanProcessor())
    set_tracer_provider(trace_provider)
    print("✅ LangSmith tracing enabled")

setup_langsmith()

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    AudioConfig,
    BackgroundAudioPlayer,
    BuiltinAudioClip,
    JobContext,
    cli,
    room_io,
)
from livekit.plugins import cartesia, sarvam, langchain
from langgraph_agent import create_calendar_graph

logger = logging.getLogger("calendar-agent")
class CalendarAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly, reliable voice assistant that answers questions, explains topics, and completes tasks with available tools.""",
            tools=[EndCallTool(
                extra_description="""""",
                end_instructions="""Thank the user for their time and say goodbye.""",
                delete_room=True,
            )],
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="""Greet the user and offer your assistance.""",
            allow_interruptions= True,
        )

server = AgentServer()


@server.rtc_session(agent_name="CalendarAgent")
async def entrypoint(ctx: JobContext):
    session_id = str(uuid.uuid4())

    session = AgentSession(
        stt=sarvam.STT(
            language="en-IN",
            model="saaras:v3",
            mode="codemix",
            flush_signal=True,       
        ),
        llm=langchain.LLMAdapter(
            graph=create_calendar_graph(),
            config={"configurable": {"thread_id": session_id}},
            stream_mode="custom",   
        ),
        tts=sarvam.TTS(
            target_language_code="en-IN",  
            model="bulbul:v3",
            speaker="shubh"
        ),
        turn_detection="stt",         
        min_endpointing_delay=0.8,    
        preemptive_generation=False, 
    )



    await session.start(
        agent=CalendarAgent(),
        room=ctx.room,
    )

    async def publish_ui_event(event_type: str, data: dict):
        try:
            payload = json.dumps({"type": event_type, **data}).encode('utf-8')
            await ctx.room.local_participant.publish_data(payload=payload, topic="ui_updates")
        except Exception as e:
            logger.error(f"Failed to publish UI event: {e}")

    @session.on("agent_state_changed")
    def on_agent_state(ev):
        # Convert Enum to string safely
        new_state_str = str(getattr(ev, "new_state", "")).split(".")[-1].lower()
        asyncio.create_task(publish_ui_event("agent_state", {"state": new_state_str}))

    background_audio = BackgroundAudioPlayer(
        ambient_sound=AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=1.0),
    )
    await background_audio.start(room=ctx.room, agent_session=session)


if __name__ == "__main__":
    cli.run_app(server)