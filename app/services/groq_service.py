from groq import AsyncGroq
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.client = None
        if settings.groq_api_key:
            self.client = AsyncGroq(api_key=settings.groq_api_key)

    async def transcribe_audio(self, audio_bytes: bytes):
        """Low-latency STT using Groq Whisper (In-memory)"""
        if not self.client:
            return None
            
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav" # Groq requires a filename extension
        
        try:
            transcription = await self.client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="text"
            )
            return transcription
        except Exception as e:
            logger.error(f"Groq transcription error: {e}")
            return None

    async def analyze_text(self, text: str):
        """Use Groq for deep analysis of the curse/intent"""
        if not self.client:
            return None
            
        chat_completion = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI specialized in detecting profanity and toxic speech in multilingual environments, specifically English, Hindi, and Hinglish (code-switching).
                    Analyze the following text. If it contains offensive language, abuse, or curses in ANY of these languages, return only the word 'TOXIC'.
                    Otherwise, return 'CLEAN'.
                    Be strict with Hindi slang and regional curses."""
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return chat_completion.choices[0].message.content

groq_service = GroqService()
