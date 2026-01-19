from typing import Optional
from pydantic import BaseModel


class SpeechTranscribeResponse(BaseModel):
    success: bool
    transcript: Optional[str] = None
    error: Optional[str] = None
