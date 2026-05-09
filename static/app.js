document.addEventListener('DOMContentLoaded', () => {
    const connectBtn = document.getElementById('connect-btn');
    const statusText = document.getElementById('connection-status');
    const agentOrb = document.getElementById('agent-orb');
    const agentStateText = document.getElementById('agent-state-text');

    let room = null;
    let activeToolCards = {}; 

    connectBtn.addEventListener('click', async () => {
        if (room && room.state === 'connected') {
            await room.disconnect();
            updateUIState('disconnected');
            return;
        }

        try {
            connectBtn.disabled = true;
            statusText.innerText = "Fetching token...";
            
            // 1. Fetch Token from FastAPI server
            const response = await fetch('/token');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            const { token, url } = data;
            
            statusText.innerText = "Connecting to LiveKit...";

            // 2. Connect to LiveKit Room
            room = new LivekitClient.Room();
            
            // Set up event listeners BEFORE connecting
            room.on(LivekitClient.RoomEvent.DataReceived, (payload, participant, kind, topic) => {
                if (topic === "ui_updates") {
                    handleUIUpdate(payload);
                }
            });

            // Handle incoming audio/video tracks
            room.on(LivekitClient.RoomEvent.TrackSubscribed, (track, publication, participant) => {
                if (track.kind === 'audio' || track.kind === 'video') {
                    // Attach the track to a new HTML media element and append it to the body so it plays
                    const element = track.attach();
                    document.body.appendChild(element);
                }
            });

            // Handle native transcriptions (fallback and primary for streaming text)
            room.on(LivekitClient.RoomEvent.TranscriptionReceived, (segments, participant) => {
                const finalSegments = segments.filter(s => s.isFinal);
                if (finalSegments.length === 0) return;
                
                const text = finalSegments.map(s => s.text).join(' ').trim();
                if (!text) return;
                
                if (participant && participant.isLocal) {
                    addMessage('user', text);
                } else {
                    addMessage('agent', text);
                }
            });

            // Handle tracks being removed
            room.on(LivekitClient.RoomEvent.TrackUnsubscribed, (track) => {
                track.detach();
            });

            room.on(LivekitClient.RoomEvent.Disconnected, () => {
                updateUIState('disconnected');
            });

            await room.connect(url, token);
            
            // Automatically enable the microphone so the agent can hear the user
            await room.localParticipant.setMicrophoneEnabled(true);
            
            updateUIState('connected');
            statusText.innerText = "Connected to Agent Room";
            connectBtn.disabled = false;

        } catch (error) {
            console.error("Connection failed:", error);
            statusText.innerText = "Error: " + error.message;
            connectBtn.disabled = false;
        }
    });

    function updateUIState(state) {
        if (state === 'connected') {
            connectBtn.innerText = "Disconnect";
            connectBtn.style.background = "#ef4444";
            agentOrb.className = "orb listening";
            agentStateText.innerText = "Listening";
        } else {
            connectBtn.innerText = "Connect to Agent";
            connectBtn.style.background = "var(--accent-color)";
            agentOrb.className = "orb disconnected";
            agentStateText.innerText = "Disconnected";
            statusText.innerText = "Waiting to connect...";
        }
    }

    function handleUIUpdate(payloadBytes) {
        try {
            const decoder = new TextDecoder("utf-8");
            const jsonString = decoder.decode(payloadBytes);
            const event = JSON.parse(jsonString);
            
            console.log("UI Event:", event);

            switch (event.type) {
                case "agent_state":
                    agentOrb.className = `orb ${event.state}`;
                    agentStateText.innerText = event.state;
                    break;
            }
        } catch (e) {
            console.error("Failed to parse data channel message", e);
        }
    }
});
