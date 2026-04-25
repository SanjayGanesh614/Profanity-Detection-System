import streamlit as st
import pyaudio
import websockets
import asyncio
import json
import winsound
import time
import pandas as pd
from datetime import datetime
from app.database import engine, SessionLocal, Base
from app.models import Log, User
from sqlalchemy import desc

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Configuration
WS_URL = "ws://localhost:8000/ws/audio"
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Set Page Config
st.set_page_config(page_title="Spazor | Real-time Monitor", page_icon="🛡️", layout="wide")

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
            padding: 40px 20px;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }}
        .speaker-label {{
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 5px;
        }}
        .speaker-name {{
            font-size: 2.5rem;
            color: #ffffff;
            margin-bottom: 15px;
            font-weight: 800;
            font-family: 'Inter', sans-serif;
        }}
        .transcript-text {{
            font-size: 1.4rem;
            color: rgba(255, 255, 255, 0.9);
            font-style: italic;
            max-width: 90%;
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
        .log-table {{
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            padding: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'alert_end' not in st.session_state:
    st.session_state.alert_end = 0
if 'speaker' not in st.session_state:
    st.session_state.speaker = "Idle"
if 'transcript' not in st.session_state:
    st.session_state.transcript = "Click start to begin monitoring."
if 'user_names' not in st.session_state:
    st.session_state.user_names = {}
    # Load from DB
    db = SessionLocal()
    users = db.query(User).all()
    for u in users:
        st.session_state.user_names[u.speaker_id] = u.name
    db.close()

async def run_monitor():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    placeholder = st.empty()
    log_placeholder = st.empty()
    
    try:
        async with websockets.connect(WS_URL) as ws:
            while st.session_state.monitoring:
                # Calculate if we should be in alert mode
                is_alert = time.time() < st.session_state.alert_end
                apply_style(is_alert)
                
                # Render the UI
                with placeholder.container():
                    display_name = st.session_state.user_names.get(st.session_state.speaker, st.session_state.speaker)
                    st.markdown(f"""
                        <div class="monitor-card">
                            <div class="speaker-label">Detected Speaker</div>
                            <div class="speaker-name">{display_name}</div>
                            <div class="transcript-text">"{st.session_state.transcript}"</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 20px; font-weight: 500; opacity: 0.8;">
                            <span class="status-indicator"></span> 
                            {"VIOLATION DETECTED" if is_alert else "MONITORING ACTIVE"}
                        </div>
                    """, unsafe_allow_html=True)

                # Capture and Stream Audio
                data = stream.read(CHUNK, exception_on_overflow=False)
                await ws.send(data)
                
                # Receive feedback
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=0.001)
                    res = json.loads(msg)
                    if res.get("status") == "processed":
                        st.session_state.speaker = res.get("speaker_id", "Unknown")
                        st.session_state.transcript = res.get("text", "")
                        
                        if res.get("is_violation"):
                            st.session_state.alert_end = time.time() + 2.5
                            winsound.Beep(1200, 200)
                except asyncio.TimeoutError:
                    pass
                
                # Periodically update logs from DB
                with log_placeholder.container():
                    st.markdown("### 📋 Recent Violations (Live DB)")
                    db = SessionLocal()
                    logs = db.query(Log).order_by(desc(Log.timestamp)).limit(5).all()
                    if logs:
                        data = []
                        for l in logs:
                            s_name = st.session_state.user_names.get(l.speaker_id, l.speaker_id)
                            data.append({
                                "Time": l.timestamp.strftime("%H:%M:%S"),
                                "Speaker": s_name,
                                "Transcript": l.transcript,
                                "Toxicity": f"{l.toxicity_score:.2f}",
                                "Violation": "🔴" if l.is_violation else "🟢"
                            })
                        st.table(pd.DataFrame(data))
                    db.close()

                await asyncio.sleep(0.01)

    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.session_state.monitoring = False
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def main():
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️ Spazor Live</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7; margin-bottom: 30px;'>Next-Gen Profanity Detection & Speaker ID</p>", unsafe_allow_html=True)
    
    sidebar = st.sidebar
    sidebar.title("Settings")
    
    # Start/Stop Button
    if st.session_state.monitoring:
        if sidebar.button("STOP MONITORING", type="primary", use_container_width=True):
            st.session_state.monitoring = False
            st.rerun()
    else:
        if sidebar.button("START MONITORING", type="primary", use_container_width=True):
            st.session_state.monitoring = True
            st.rerun()

    # User Naming Section
    sidebar.markdown("---")
    sidebar.subheader("Name Speakers")
    new_speaker_id = sidebar.text_input("Speaker ID (e.g., Speaker_X)")
    new_name = sidebar.text_input("Assign Name")
    if sidebar.button("Save Mapping"):
        if new_speaker_id and new_name:
            # Update Session State
            st.session_state.user_names[new_speaker_id] = new_name
            
            # Update Database
            db = SessionLocal()
            existing_user = db.query(User).filter(User.speaker_id == new_speaker_id).first()
            if existing_user:
                existing_user.name = new_name
            else:
                db.add(User(speaker_id=new_speaker_id, name=new_name))
            db.commit()
            db.close()
            
            st.success(f"Mapped {new_speaker_id} to {new_name}")

    if st.session_state.monitoring:
        asyncio.run(run_monitor())
    else:
        apply_style(False)
        st.markdown(f"""
            <div class="monitor-card" style="margin-top: 50px;">
                <div class="speaker-label">System Status</div>
                <div class="speaker-name">Standby</div>
                <div class="transcript-text">Monitoring is currently inactive. Click 'Start' in the sidebar to begin.</div>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
