from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.toxicity import classifier
from app.services.monitoring import process_violation
from app.services.transcription import transcription_service
from app.services.speaker import speaker_service
from app.services.alerts import alert_service
from app.services.groq_service import groq_service
import json
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    # Ultra-low latency buffer: ~0.75 seconds (16000 * 2 * 0.75 = 24000 bytes)
    BUFFER_LIMIT = 24000 
    audio_buffer = bytearray()
    
    try:
        while True:
            message = await websocket.receive()
            
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    speaker_id = data.get("speaker_id", "unknown")
                    text = data.get("text", "")
                    if text:
                        await handle_text_processing(text, speaker_id, db, websocket)
                except json.JSONDecodeError:
                    pass
            
            elif "bytes" in message:
                audio_chunk = message["bytes"]
                audio_buffer.extend(audio_chunk)
                
                if len(audio_buffer) >= BUFFER_LIMIT:
                    # Capture buffer for async processing
                    current_audio_pcm = bytes(audio_buffer)
                    audio_buffer = bytearray() # Clear immediately
                    
                    # 1. Convert PCM to WAV in-memory for the Cloud API
                    from pydub import AudioSegment
                    import io

                    try:
                        audio_segment = AudioSegment.from_raw(
                            io.BytesIO(current_audio_pcm),
                            sample_width=2,
                            frame_rate=16000,
                            channels=1
                        )
                        
                        # Export to WAV in memory
                        wav_io = io.BytesIO()
                        audio_segment.export(wav_io, format="wav")
                        wav_bytes = wav_io.getvalue()

                        # 2. Transcribe via Cloud (Groq)
                        if groq_service.client:
                            text = await groq_service.transcribe_audio(wav_bytes)
                        else:
                            # Fallback to local
                            text = transcription_service.transcribe(current_audio_pcm)
                        
                        if text and len(text.strip()) > 1:
                            logger.info(f"Transcribed: {text}")
                            # 3. Identify speaker
                            speaker_id = await speaker_service.identify_speaker(current_audio_pcm, transcript=text)
                            # 4. Process
                            await handle_text_processing(text, speaker_id, db, websocket)
                    except Exception as e:
                        logger.error(f"Processing error: {e}")
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if not websocket.client_state.name == "DISCONNECTED":
            await websocket.close()

async def handle_text_processing(text: str, speaker_id: str, db: Session, websocket: WebSocket):
    # 1. Resolve Speaker Name
    from app.models import User
    user = db.query(User).filter(User.speaker_id == speaker_id).first()
    display_name = user.name if user else speaker_id

    # 2. Analyze for Toxicity (Hindi-aware)
    is_toxic = False
    score = 0.0
    
    if groq_service.client:
        # Use Groq for smarter, Hindi-aware detection
        analysis = await groq_service.analyze_text(text)
        # Simple parsing logic for Groq response
        is_toxic = "TOXIC" in analysis.upper() or "VIOLATION" in analysis.upper()
        score = 1.0 if is_toxic else 0.0
    else:
        # Fallback to local XLM-R model
        score = float(classifier.analyze(text))
        is_toxic = score >= 0.5
    
    # 3. Process and save
    db_log = await process_violation(
        db=db,
        speaker_id=speaker_id,
        transcript=text,
        toxicity_score=score
    )
    
    # Force the is_violation based on our smarter logic if needed
    if is_toxic != db_log.is_violation:
        db_log.is_violation = is_toxic
        db.commit()

    # 4. Trigger Alert
    if db_log.is_violation:
        logger.info(f"VIOLATION DETECTED from {display_name}: {text}")
        alert_service.play_ping()
        # Send Discord Alert in the background
        asyncio.create_task(alert_service.send_discord_alert(text, display_name, score))
    
    # Send feedback
    await websocket.send_json({
        "status": "processed",
        "text": text,
        "speaker_id": display_name,
        "raw_speaker_id": speaker_id,
        "toxicity_score": score,
        "is_violation": db_log.is_violation
    })
