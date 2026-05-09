import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from livekit import api
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/token")
async def get_token(participant_name: str = "User"):
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    livekit_url = os.getenv("LIVEKIT_URL")

    if not livekit_api_key or not livekit_api_secret:
        return {"error": "LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env"}

    token = api.AccessToken(livekit_api_key, livekit_api_secret) \
        .with_identity(participant_name) \
        .with_name(participant_name) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room="my-agent-room",
        ))

    # Explicitly dispatch the agent to join the room
    from livekit.protocol.agent_dispatch import CreateAgentDispatchRequest
    try:
        async with api.LiveKitAPI() as lkapi:
            await lkapi.agent_dispatch.create_dispatch(CreateAgentDispatchRequest(
                agent_name="CalendarAgent",
                room="my-agent-room"
            ))
    except Exception as e:
        print(f"Agent dispatch notice: {e}")

    return {
        "token": token.to_jwt(),
        "url": livekit_url
    }
