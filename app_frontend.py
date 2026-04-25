import streamlit as st
import pyaudio
import websockets
import asyncio
import json
import winsound
import time

# Configuration
WS_URL = "ws://localhost:8000/ws/audio"
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Set Page Config
st.set_page_config(page_title="Curse Monitor", page_icon="🛡️", layout="centered")

# Custom CSS for the Minimalist Premium Look
def apply_style(alert=False):
    bg_color = "#b91c1c" if alert else "#0f172a"
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {bg_color};
            transition: background-color 0.4s ease-in-out;
            color: white;
        }}
        .monitor-card {{
            background-color: rgba(255, 255, 255, 0.05);
            padding: 50px 20px;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            margin-top: 50px;
        }}
        .speaker-label {{
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 5px;
        }}
        .speaker-name {{
            font-size: 3.5rem;
            color: #ffffff;
            margin-bottom: 20px;
            font-weight: 800;
            font-family: 'Inter', sans-serif;
        }}
        .transcript-text {{
            font-size: 1.8rem;
            color: rgba(255, 255, 255, 0.9);
            font-style: italic;
            max-width: 80%;
            margin: 0 auto;
            line-height: 1.4;
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: {"#ef4444" if alert else "#10b981"};
            border-radius: 50%;
            margin-right: 8px;
            box-shadow: 0 0 10px {"#ef4444" if alert else "#10b981"};
        }}
        </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'alert_end' not in st.session_state:
    st.session_state.alert_end = 0
if 'speaker' not in st.session_state:
    st.session_state.speaker = "Idle"
if 'transcript' not in st.session_state:
    st.session_state.transcript = "Click start to begin monitoring your environment."

async def run_monitor():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    placeholder = st.empty()
    
    try:
        async with websockets.connect(WS_URL) as ws:
            while True:
                # Calculate if we should be in alert mode
                is_alert = time.time() < st.session_state.alert_end
                apply_style(is_alert)
                
                # Render the UI
                with placeholder.container():
                    st.markdown(f"""
                        <div class="monitor-card">
                            <div class="speaker-label">Detected Speaker</div>
                            <div class="speaker-name">{st.session_state.speaker}</div>
                            <div class="transcript-text">"{st.session_state.transcript}"</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div style="text-align: center; margin-top: 30px; font-weight: 500; opacity: 0.8;">
                            <span class="status-indicator"></span> 
                            {"VIOLATION DETECTED" if is_alert else "MONITORING ACTIVE"}
                        </div>
                    """, unsafe_allow_html=True)

                # Capture and Stream Audio
                data = stream.read(CHUNK, exception_on_overflow=False)
                await ws.send(data)
                
                # Non-blocking receive for feedback
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=0.005)
                    res = json.loads(msg)
                    if res.get("status") == "processed":
                        st.session_state.speaker = res.get("speaker_id", "Unknown")
                        st.session_state.transcript = res.get("text", "")
                        
                        if res.get("is_violation"):
                            st.session_state.alert_end = time.time() + 2.5 # Glow red for 2.5s
                            winsound.Beep(1200, 400) # Ping noise
                except asyncio.TimeoutError:
                    pass
                
                await asyncio.sleep(0.01)

    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.info("Ensure the backend is running with 'python -m app.main'")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def main():
    st.markdown("<h1 style='text-align: center;'>🛡️ Spazor Live</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>Minimalist AI Curse Monitoring System</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("START MONITOR", use_container_width=True, type="primary"):
            asyncio.run(run_monitor())
        else:
            apply_style(False)
            st.markdown(f"""
                <div class="monitor-card">
                    <div class="speaker-label">Status</div>
                    <div class="speaker-name">Ready</div>
                    <div class="transcript-text">Waiting for input stream...</div>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
