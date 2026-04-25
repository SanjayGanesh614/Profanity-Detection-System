This project involves creating a **Real-time Multilingual Profanity Monitoring System** with a distributed architecture using an **ESP32** edge node and a central **AI Processing Server**.

### **Project Overview**
The system captures environmental audio via an ESP32, streams it to a server for multilingual transcription (Hindi, English, and regional dialects), analyzes the text for toxicity, identifies the specific speaker using voice biometrics, and logs violations with automated alerts.

---

### **Technical Stack & Components**

#### **1. Edge Layer (The Hardware)**
* **Microcontroller:** ESP32 (WROOM/S3) for Wi-Fi connectivity and I2S processing.
* **Audio Capture:** INMP441 MEMS Microphone (Digital I2S) for high-fidelity audio without analog noise.
* **Communication:** WebSockets or UDP for low-latency, real-time PCM audio streaming to the server.

#### **2. Processing Layer (The AI Server)**
This can run on a laptop (GPU-accelerated) or as a Cloud API service.
* **Automatic Speech Recognition (ASR):**
    * **OpenAI Whisper (large-v3):** For high-accuracy English/Hinglish transcription.
    * **AI4Bharat Indic-Conformer:** For superior accuracy in regional Indian languages.
* **Natural Language Processing (NLP):**
    * **Transformer-based Toxicity Classifier:** (e.g., `xlm-roberta-large` fine-tuned for toxicity) to detect offensive intent across code-switching (Hinglish).
* **Speaker Recognition (The "Flagging" Logic):**
    * **Pyannote.audio:** Used for **Diarization** (separating voices) and **Embedding Extraction** (creating a unique voice fingerprint for each user).

#### **3. Backend & Logging Layer**
* **Database:** SQLite or PostgreSQL to store logs containing `timestamp`, `speaker_id`, `transcript`, and `toxicity_score`.
* **Alert System:** Integration via Webhooks (Discord/Slack) or Pushover for real-time "ping" notifications when a violation is detected.

---

### **The Technical Workflow**
1.  **Ingestion:** ESP32 captures audio at 16kHz and streams it in chunks.
2.  **Transcription:** The server reconstructs audio and passes it through the ASR model to generate text.
3.  **Toxicity Scoring:** The NLP model checks the text. If the probability $P(\text{toxic}) > \text{threshold}$, the event is flagged.
4.  **Speaker Mapping:** The audio segment is compared against a vector database of pre-enrolled voice embeddings to identify the offender.
5.  **Execution:** The system logs the data and triggers a remote ping.

