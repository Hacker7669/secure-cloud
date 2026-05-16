# =============================================================================
# utils/s3.py — AWS S3 upload / download / presigned URL helpers
# =============================================================================
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError

from config import Config

_client = None


def _ensure_s3_config() -> None:
    if not Config.BUCKET_NAME:
        raise RuntimeError("S3 bucket name is missing")
    if not Config.AWS_ACCESS_KEY or not Config.AWS_SECRET_KEY:
        raise RuntimeError("AWS credentials are not configured")


def _get_client():
    global _client
    if _client is None:
        _ensure_s3_config()
        _client = boto3.client(
            "s3",
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY,
            region_name=Config.AWS_REGION,
        )
    return _client


def _safe_filename(filename: str) -> str:
    cleaned = Path(filename or "file.bin").name.strip()
    return cleaned or "file.bin"


def upload_bytes_to_s3(data: bytes, filename: str, mime_type: str = "application/octet-stream") -> str:
    """Upload raw encrypted bytes to S3 and return the object key."""
    if not isinstance(data, (bytes, bytearray)):
        raise RuntimeError("Upload payload must be bytes")
    payload = bytes(data)
    if len(payload) == 0:
        raise RuntimeError("Refusing to upload empty payload")

    client = _get_client()
    object_key = f"encrypted/{uuid.uuid4().hex}_{_safe_filename(filename)}"
    try:
        client.put_object(
            Bucket=Config.BUCKET_NAME,
            Key=object_key,
            Body=payload,
            ContentType=mime_type or "application/octet-stream",
            ContentLength=len(payload),
            ServerSideEncryption="AES256",
        )
        return object_key
    except (NoCredentialsError, PartialCredentialsError):
        raise RuntimeError("AWS credentials are not configured")
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"S3 upload failed: {exc}")


def download_from_s3(key: str) -> bytes:
    """Download object bytes from S3."""
    if not key:
        raise RuntimeError("S3 key is missing")

    client = _get_client()
    try:
        response = client.get_object(Bucket=Config.BUCKET_NAME, Key=key)
        body = response["Body"].read()
        return body if isinstance(body, bytes) else bytes(body)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"S3 download failed: {exc}")


def generate_presigned_url(key: str, expires_in: int = 900) -> str:
    """Generate a temporary presigned URL for S3 object download."""
    if not key:
        raise RuntimeError("S3 key is missing")
    client = _get_client()
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": Config.BUCKET_NAME, "Key": key},
            ExpiresIn=max(60, int(expires_in)),
        )
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"Could not generate presigned URL: {exc}")
