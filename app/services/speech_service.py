import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from uuid import UUID

from google.cloud import storage
from google.cloud import speech

from app.config import settings


# Supported audio formats with their Speech-to-Text encoding
SUPPORTED_AUDIO_FORMATS = {
    ".wav": {
        "content_types": ["audio/wav", "audio/x-wav", "audio/wave"],
        "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
    },
    ".webm": {
        "content_types": ["audio/webm"],
        "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
    },
    ".mp3": {
        "content_types": ["audio/mpeg", "audio/mp3"],
        "encoding": speech.RecognitionConfig.AudioEncoding.MP3,
    },
    ".m4a": {
        "content_types": ["audio/m4a", "audio/mp4", "audio/x-m4a"],
        "encoding": speech.RecognitionConfig.AudioEncoding.MP3,
    },
}

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


class SpeechService:
    def __init__(self):
        self._storage_client: Optional[storage.Client] = None
        self._speech_client: Optional[speech.SpeechClient] = None

    @property
    def storage_client(self) -> storage.Client:
        if self._storage_client is None:
            self._storage_client = storage.Client()
        return self._storage_client

    @property
    def speech_client(self) -> speech.SpeechClient:
        if self._speech_client is None:
            self._speech_client = speech.SpeechClient()
        return self._speech_client

    def is_local_storage(self) -> bool:
        """Check if we should use local storage (empty static_base_url means local)."""
        return not settings.static_base_url

    def get_bucket_name(self) -> str:
        """Get bucket name from static_base_url."""
        # Example: https://storage.googleapis.com/coach-vocab-static -> coach-vocab-static
        if "coach-vocab-static-prod" in settings.static_base_url:
            return "coach-vocab-static-prod"
        return "coach-vocab-static"

    def validate_audio_format(
        self, filename: str, content_type: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate audio file format.
        Returns: (is_valid, extension, error_message)
        """
        ext = None
        for supported_ext in SUPPORTED_AUDIO_FORMATS:
            if filename.lower().endswith(supported_ext):
                ext = supported_ext
                break

        if not ext:
            return False, None, "Unsupported file format. Supported: WAV, WebM, MP3, M4A"

        return True, ext, None

    def generate_storage_path(
        self, user_id: UUID, word_id: UUID, extension: str
    ) -> str:
        """
        Generate storage path.
        Format: speech-logs/{user_id}/{timestamp}-{word_id}.{ext}
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}-{word_id}{extension}"
        return f"speech-logs/{user_id}/{filename}"

    async def save_audio(
        self, audio_data: bytes, storage_path: str, content_type: str
    ) -> str:
        """
        Save audio file to local filesystem or GCS.
        Returns: Full path (local path or gs:// URL)
        """
        if self.is_local_storage():
            return self._save_to_local(audio_data, storage_path)
        else:
            return self._upload_to_gcs(audio_data, storage_path, content_type)

    def _save_to_local(self, audio_data: bytes, storage_path: str) -> str:
        """Save audio to local static directory."""
        local_path = Path("static") / storage_path
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, "wb") as f:
            f.write(audio_data)

        return str(local_path)

    def _upload_to_gcs(
        self, audio_data: bytes, storage_path: str, content_type: str
    ) -> str:
        """Upload audio to GCS."""
        bucket_name = self.get_bucket_name()
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(storage_path)

        blob.upload_from_string(
            audio_data,
            content_type=content_type,
        )

        return f"gs://{bucket_name}/{storage_path}"

    async def transcribe_audio(
        self, audio_data: bytes, extension: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Transcribe audio using Google Cloud Speech-to-Text.
        Returns: (transcript, error_message)
        """
        try:
            format_config = SUPPORTED_AUDIO_FORMATS.get(extension)
            if not format_config:
                return None, f"Unsupported audio format: {extension}"

            encoding = format_config["encoding"]

            audio = speech.RecognitionAudio(content=audio_data)

            # For WAV files, omit sample_rate_hertz to let Google auto-detect from header
            if extension == ".wav":
                config = speech.RecognitionConfig(
                    encoding=encoding,
                    language_code="en-US",
                    enable_automatic_punctuation=False,
                )
            else:
                config = speech.RecognitionConfig(
                    encoding=encoding,
                    sample_rate_hertz=48000,
                    language_code="en-US",
                    enable_automatic_punctuation=False,
                )

            response = self.speech_client.recognize(config=config, audio=audio)

            if not response.results:
                return "", None  # No speech detected

            # Concatenate all transcript results
            transcript = " ".join(
                result.alternatives[0].transcript
                for result in response.results
                if result.alternatives
            )

            return transcript.strip(), None

        except Exception as e:
            return None, f"Transcription failed: {str(e)}"


# Singleton instance
speech_service = SpeechService()
