# 🛡️ Spazor: Real-time Multilingual Profanity Monitoring System

**Spazor** is a high-performance, distributed AI system designed to monitor environmental audio for profanity and toxic speech in real-time. By combining edge computing with a centralized AI processing server, Spazor transcribes multilingual speech, identifies specific speakers via voice biometrics, and triggers immediate alerts for violations.

![Aesthetic Dashboard Preview](https://img.shields.io/badge/UI-Premium_Glassmorphism-blueviolet?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI_%7C_Streamlit_%7C_Groq-blue?style=for-the-badge)
![Latency](https://img.shields.io/badge/Latency-Sub--Second-green?style=for-the-badge)

---

## 🚀 Key Improvements & Features

- **Ultra-Low Latency STT**: Switched to **Groq Whisper-large-v3** with in-memory audio processing. Buffer reduced to **0.75s**, providing near-instantaneous transcription.
- **Hindi & Hinglish Curse Detection**: Integrated a custom LLM prompt for Groq (Llama-3) that is specialized in detecting regional Hindi slang, abuse, and code-switched profanity.
- **Dynamic Speaker Management**: A new sidebar utility allows administrators to map voice fingerprints (Speaker IDs) to real names, persisting them to a local SQLite database.
- **Active Discord Integration**: Automated notifications are dispatched to Discord via webhooks immediately upon violation detection, including the transcript and severity score.
- **Start/Stop Controls**: The dashboard now supports toggling the monitoring state to manage system resources effectively.
- **Live DB Logging**: All violations are dynamically stored and displayed in a real-time monitoring table.

---

## 🛠️ Architecture & Tech Stack

### **1. Capture & Streaming**
- **Hardware**: Compatible with ESP32 (WROOM/S3) or local microphone inputs.
- **Protocol**: 16kHz Mono PCM streaming via WebSockets.
- **Buffer Optimization**: Uses 24,000-byte chunks (~0.75s) to balance context window and speed.

### **2. Intelligence Layer (AI Server)**
- **Transcription**: Groq Cloud API (Whisper-large-v3) for speed, with local `faster-whisper` fallback.
- **Analysis**: Groq Llama-3-8b for high-accuracy multilingual toxicity detection.
- **Biometrics**: `pyannote.audio` for speaker identification and voice mapping.

### **3. Infrastructure**
- **Backend**: FastAPI (Asynchronous WebSocket handling).
- **Database**: SQLAlchemy + SQLite for persistent user naming and violation history.
- **Frontend**: Streamlit with custom CSS (Glassmorphism, dynamic alert states).

---

## 📂 Project Structure

```text
├── app/
│   ├── api/            # WebSocket logic & Audio processing
│   ├── services/       # AI Engines (Groq, Toxicity, Speaker ID, Alerts)
│   ├── models.py       # User & Log Database Schemas
│   ├── database.py     # SQLAlchemy Setup
│   └── config.py       # Environment Configuration
├── app_frontend.py     # Streamlit Dashboard (Glassmorphic UI)
├── requirements.txt    # Python dependencies
└── .env                # API Keys & Discord Webhooks
```

---

## ⚙️ Setup & Deployment

### **1. Installation**
```bash
# Clone and enter repo
git clone https://github.com/SanjayGanesh614/Profanity-Detection-System.git
cd Profanity-Detection-System

# Setup Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Configuration**
Update your `.env` file:
```env
GROQ_API_KEY=gsk_xxx...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DATABASE_URL=sqlite:///./spazor.db
```

### **3. Execution**
```bash
# Terminal 1: Start Backend
python -m app.main

# Terminal 2: Start Frontend
streamlit run app_frontend.py
```

---

## 🛡️ Security & Privacy
- **Privacy First**: Optional local inference mode using `faster-whisper` and local RoBERTa models for sensitive environments.
- **Audit Trails**: Every violation is logged with a timestamp, speaker fingerprint, and raw transcript for forensic review.

---

**Maintained by**: Sanjay Ganesh & Team
