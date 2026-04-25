from faster_whisper import WhisperModel
import io
import numpy as np
from pydub import AudioSegment

class TranscriptionService:
    def __init__(self, model_size="base"):
        # Run on GPU with FP16 if available, otherwise CPU with int8
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_bytes: bytes):
        # Convert bytes to numpy array
        # Assuming raw PCM 16-bit 16kHz audio from ESP32
        audio_segment = AudioSegment.from_raw(
            io.BytesIO(audio_bytes),
            sample_width=2,
            frame_rate=16000,
            channels=1
        )
        
        # Convert to float32 numpy array as required by faster-whisper
        samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32) / 32768.0
        
        segments, info = self.model.transcribe(samples, beam_size=5)
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
            
        return full_text.strip()

transcription_service = TranscriptionService()
