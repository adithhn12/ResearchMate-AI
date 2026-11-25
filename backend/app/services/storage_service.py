import logging
import os
from typing import Optional
import httpx
from app.config import settings

logger = logging.getLogger("researchmate.storage")


class SupabaseStorageService:
    """
    Lightweight Supabase Storage client using httpx so uploaded PDFs are stored
    remotely in Supabase Storage while Render's local filesystem stays temporary only.
    """

    def __init__(self):
        self.base_url = settings.SUPABASE_URL
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket = settings.SUPABASE_STORAGE_BUCKET

    def is_configured(self) -> bool:
        return bool(self.base_url and self.service_key and self.bucket)

    def _headers(self, content_type: Optional[str] = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def upload_pdf(self, local_file_path: str, object_key: str) -> str:
        """
        Stream a temporary local PDF file to Supabase Storage.
        Returns the remote storage path (object_key).
        """
        if not self.is_configured():
            raise RuntimeError(
                "Supabase Storage is not configured (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing)."
            )

        clean_key = object_key.lstrip("/")
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{clean_key}"
        headers = self._headers("application/pdf")
        headers["x-upsert"] = "true"

        with open(local_file_path, "rb") as f:
            resp = httpx.post(url, content=f, headers=headers, timeout=60.0)

        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Supabase Storage upload failed (HTTP {resp.status_code}): {resp.text[:300]}"
            )

        return clean_key

    def delete_pdf(self, object_key: str) -> None:
        """Delete a PDF object from Supabase Storage."""
        if not self.is_configured() or not object_key:
            return
        clean_key = object_key.lstrip("/")
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{clean_key}"
        try:
            resp = httpx.delete(url, headers=self._headers(), timeout=30.0)
            if resp.status_code not in (200, 204, 404):
                logger.warning(
                    f"Supabase Storage delete returned HTTP {resp.status_code} for {clean_key}: {resp.text[:200]}"
                )
        except Exception as exc:
            logger.warning(f"Failed to delete {clean_key} from Supabase Storage: {exc}")


storage_service = SupabaseStorageService()
