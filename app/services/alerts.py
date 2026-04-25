try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

import os
import logging

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
                winsound.Beep(1000, 500)
                logger.info("Played alert beep.")
            except Exception as e:
                logger.error(f"Failed to play sound: {e}")
        else:
            logger.warning("Alert sound requested but winsound not available.")

alert_service = AlertService()
