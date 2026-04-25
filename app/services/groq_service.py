from groq import AsyncGroq
from app.config import settings

class GroqService:
    def __init__(self):
        self.client = None
        if settings.groq_api_key:
            self.client = AsyncGroq(api_key=settings.groq_api_key)

    async def transcribe_audio(self, audio_file_path: str):
        """Alternative STT using Groq Whisper (very fast)"""
        if not self.client:
            return None
            
        with open(audio_file_path, "rb") as file:
            transcription = await self.client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        return transcription

    async def analyze_text(self, text: str):
        """Use Groq for deep analysis of the curse/intent"""
        if not self.client:
            return None
            
        chat_completion = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that analyzes transcriptions for offensive content. Categorize the type of curse and its severity."
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content

groq_service = GroqService()
