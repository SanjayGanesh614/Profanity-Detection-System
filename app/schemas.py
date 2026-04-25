from pydantic import BaseModel
from datetime import datetime

class LogCreate(BaseModel):
    speaker_id: str
    transcript: str
    toxicity_score: float

class LogResponse(BaseModel):
    id: str
    timestamp: datetime
    speaker_id: str
    transcript: str
    toxicity_score: float
    is_violation: bool

    model_config = {"from_attributes": True}

class AudioEvent(BaseModel):
    speaker_id: str
    text: str
