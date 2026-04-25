import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

async def send_discord_alert(speaker_id: str, transcript: str, score: float):
    if not settings.discord_webhook_url:
        return

    content = f"🚨 **Profanity Alert!** 🚨\n**Speaker:** {speaker_id}\n**Toxicity Score:** {score:.2f}\n**Transcript:** \"{transcript}\""
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(settings.discord_webhook_url, json={"content": content})
    except Exception as e:
        logger.error(f"Failed to send Discord alert: {e}")
