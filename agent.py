import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import logging
import uuid
import os

from dotenv import load_dotenv
load_dotenv()
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
from livekit.plugins import sarvam, langchain
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

    DB_URI = os.getenv("DATABASE_URL")
    
    if DB_URI:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
            await checkpointer.setup()
            await _run_session(ctx, session_id, checkpointer)
    else:
        await _run_session(ctx, session_id, None)

async def _run_session(ctx: JobContext, session_id: str, checkpointer):
    session = AgentSession(
        stt=sarvam.STT(
            language="en-IN",
            model="saaras:v3",
            mode="codemix",
            flush_signal=True,       
        ),
        llm=langchain.LLMAdapter(
            graph=create_calendar_graph(checkpointer),
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
    
    background_audio = BackgroundAudioPlayer(
        ambient_sound=AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=1.0),
    )
    await background_audio.start(room=ctx.room, agent_session=session)
    
    # Wait until the room is disconnected to keep the checkpointer pool alive
    shutdown_event = asyncio.Event()
    ctx.room.on("disconnected", lambda *args: shutdown_event.set())
    await shutdown_event.wait()


if __name__ == "__main__":
    cli.run_app(server)