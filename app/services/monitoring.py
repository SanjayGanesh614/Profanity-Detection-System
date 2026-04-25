from sqlalchemy.orm import Session
from app.models import Log
from app.schemas import LogCreate
from app.config import settings
from app.services.webhook import send_discord_alert

async def process_violation(db: Session, speaker_id: str, transcript: str, toxicity_score: float):
    is_violation = toxicity_score >= settings.toxicity_threshold

    # Log to DB
    db_log = Log(
        speaker_id=speaker_id,
        transcript=transcript,
        toxicity_score=toxicity_score,
        is_violation=is_violation
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Fire Webhook if Violation
    if is_violation:
        await send_discord_alert(speaker_id, transcript, toxicity_score)

    return db_log
