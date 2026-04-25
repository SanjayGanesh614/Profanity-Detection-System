from app.services.groq_service import groq_service
import logging

logger = logging.getLogger(__name__)

class SpeakerService:
    def __init__(self):
        pass

    async def identify_speaker(self, audio_bytes: bytes, transcript: str = ""):
        """
        Identify the speaker from the audio or transcript.
        If transcript is provided, use Groq to attempt to tag the person.
        """
        if not transcript:
            return "Unknown_Speaker"

        # Use Groq to try and 'tag' the person based on text context
        try:
            prompt = f"Based on this transcript: '{transcript}', can you identify or tag the speaker? If they mention a name, return only that name. Otherwise return a generic tag like 'Speaker_A' or 'Participant'. Return ONLY the tag."
            tag = await self._get_tag_from_groq(prompt)
            return tag.strip() if tag else "Speaker_X"
        except Exception as e:
            logger.error(f"Error in speaker tagging: {e}")
            return "Speaker_X"

    async def _get_tag_from_groq(self, prompt: str):
        if not groq_service.client:
            return "Speaker_X"
        
        completion = await groq_service.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return completion.choices[0].message.content

speaker_service = SpeakerService()
