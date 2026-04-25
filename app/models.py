from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    speaker_id = Column(String, index=True)
    transcript = Column(String)
    toxicity_score = Column(Float)
    is_violation = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"

    speaker_id = Column(String, primary_key=True, index=True)
    name = Column(String)
