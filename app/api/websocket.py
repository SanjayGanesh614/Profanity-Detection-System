from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.toxicity import classifier
from app.services.monitoring import process_violation
from app.services.transcription import transcription_service
from app.services.speaker import speaker_service
from app.services.alerts import alert_service
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    # We'll use a simple buffer for demonstration. 
    # In production, we'd use a more sophisticated voice activity detection (VAD).
    audio_buffer = bytearray()
    
    try:
        while True:
            # Receive data (can be text/JSON or binary audio)
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
                
                # If we have enough audio (e.g., > 3 seconds at 16kHz 16-bit)
                # 16000 * 2 * 3 = 96000 bytes
                if len(audio_buffer) >= 96000:
                    # 1. Transcribe
                    text = transcription_service.transcribe(bytes(audio_buffer))
                    logger.info(f"Transcribed: {text}")
                    
                    # 2. Identify speaker
                    speaker_id = await speaker_service.identify_speaker(bytes(audio_buffer), transcript=text)
                    
                    if text:
                        await handle_text_processing(text, speaker_id, db, websocket)
                    
                    # Clear buffer after processing
                    audio_buffer = bytearray()
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if not websocket.client_state.name == "DISCONNECTED":
            await websocket.close()

async def handle_text_processing(text: str, speaker_id: str, db: Session, websocket: WebSocket):
    # 1. Analyze text for toxicity
    score = classifier.analyze(text)
    
    # 2. Process and save violation
    db_log = await process_violation(
        db=db,
        speaker_id=speaker_id,
        transcript=text,
        toxicity_score=score
    )
    
    # 3. If it's a violation, trigger ping
    if db_log.is_violation:
        logger.info(f"VIOLATION DETECTED from {speaker_id}: {text}")
        alert_service.play_ping()
    
    # Send feedback back to client
    await websocket.send_json({
        "status": "processed",
        "text": text,
        "speaker_id": speaker_id,
        "toxicity_score": score,
        "is_violation": db_log.is_violation
    })
