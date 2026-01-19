from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.speech_log import SpeechLog
from app.schemas.speech import SpeechTranscribeResponse
from app.repositories.word_repository import WordRepository
from app.services.speech_service import speech_service, MAX_FILE_SIZE_BYTES

router = APIRouter(prefix="/api/speech", tags=["speech"])

VALID_PLATFORMS = {"ios", "android", "web"}


@router.post("/transcribe", response_model=SpeechTranscribeResponse)
async def transcribe_speech(
    audio: UploadFile = File(..., description="Audio file (WAV, WebM, MP3, M4A)"),
    word_id: str = Form(..., description="UUID of the word"),
    platform: str = Form(..., description="Platform: ios, android, web"),
    native_transcript: Optional[str] = Form(None, description="Device-detected transcript"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Transcribe speech audio for vocabulary practice.

    - Accepts multipart/form-data with audio file and metadata
    - Saves audio to local filesystem (dev) or GCS (production)
    - Uses Google Cloud Speech-to-Text for transcription
    - Logs the attempt for analytics
    """
    # Validate platform
    if platform not in VALID_PLATFORMS:
        return SpeechTranscribeResponse(
            success=False,
            error=f"Invalid platform. Must be one of: {', '.join(VALID_PLATFORMS)}"
        )

    # Validate word_id UUID format
    try:
        word_uuid = UUID(word_id)
    except ValueError:
        return SpeechTranscribeResponse(
            success=False,
            error="Invalid word_id format"
        )

    # Validate word exists
    word_repo = WordRepository(db)
    word = word_repo.get_by_id(word_uuid)
    if not word:
        return SpeechTranscribeResponse(
            success=False,
            error="Word not found"
        )

    # Validate audio format
    is_valid, extension, error = speech_service.validate_audio_format(
        audio.filename or "", audio.content_type or ""
    )
    if not is_valid:
        return SpeechTranscribeResponse(success=False, error=error)

    # Read audio content
    audio_data = await audio.read()

    # Validate file size
    if len(audio_data) > MAX_FILE_SIZE_BYTES:
        return SpeechTranscribeResponse(
            success=False,
            error=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB"
        )

    # Generate storage path and save
    storage_path = speech_service.generate_storage_path(
        current_user.id, word_uuid, extension
    )

    try:
        recording_path = await speech_service.save_audio(
            audio_data, storage_path, audio.content_type or "application/octet-stream"
        )
    except Exception as e:
        return SpeechTranscribeResponse(
            success=False,
            error=f"Failed to save audio: {str(e)}"
        )

    # Transcribe audio
    cloud_transcript, transcribe_error = await speech_service.transcribe_audio(
        audio_data, extension
    )

    # Log to database (even if transcription fails, we log the upload)
    speech_log = SpeechLog(
        user_id=current_user.id,
        word_id=word_uuid,
        word=word.word,
        recording_path=recording_path,
        platform=platform,
        native_transcript=native_transcript,
        cloud_transcript=cloud_transcript,
    )
    db.add(speech_log)
    db.commit()

    if transcribe_error:
        return SpeechTranscribeResponse(
            success=False,
            transcript=None,
            error=transcribe_error
        )

    return SpeechTranscribeResponse(
        success=True,
        transcript=cloud_transcript,
    )
