try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

import httpx
import logging
import os
from app.config import settings

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        # Path to a ping sound file
        self.ping_path = os.path.join(os.path.dirname(__file__), "assets", "ping.wav")

    def play_ping(self):
        """Play a notification sound when a violation occurs"""
        if HAS_WINSOUND:
            try:
                # Use a simple beep as fallback
                winsound.Beep(1000, 200)
                logger.info("Played alert beep.")
            except Exception as e:
                logger.error(f"Failed to play sound: {e}")
        else:
            logger.warning("Alert sound requested but winsound not available.")

    async def send_discord_alert(self, text: str, speaker: str, score: float):
        """Send an alert to Discord via Webhook"""
        if not settings.discord_webhook_url:
            logger.warning("Discord Webhook URL not set.")
            return

        payload = {
            "embeds": [{
                "title": "🚨 Profanity Detected!",
                "color": 15158332, # Red
                "fields": [
                    {"name": "Speaker", "value": speaker, "inline": True},
                    {"name": "Severity Score", "value": f"{score:.2f}", "inline": True},
                    {"name": "Transcript", "value": f"```{text}```", "inline": False}
                ],
                "footer": {"text": "Spazor Monitor System"}
            }]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(settings.discord_webhook_url, json=payload)
                if response.status_code == 204:
                    logger.info("Discord alert sent successfully.")
                else:
                    logger.error(f"Failed to send Discord alert: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Discord alert: {e}")

alert_service = AlertService()
