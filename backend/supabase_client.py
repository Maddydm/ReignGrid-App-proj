import os
import json
from typing import Optional, List, Dict, Any
from backend.config import (
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_ANON_KEY,
    SUPABASE_STORAGE_BUCKET,
)

class SupabaseService:
    def __init__(self):
        self._client = None
        self._init_client()

    def _init_client(self):
        """Attempt to initialize official supabase-py client if credentials exist."""
        if SUPABASE_URL and (SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY):
            try:
                from supabase import create_client
                key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
                self._client = create_client(SUPABASE_URL, key)
                print(f"[REIGNGRID] Connected to Supabase PostGIS at {SUPABASE_URL}")
            except Exception as e:
                print(f"[REIGNGRID] Warning: Unable to initialize Supabase client ({e}). Operating in standalone PostGIS GeoJSON mode.")
        else:
            print("[REIGNGRID] Notice: SUPABASE_URL / keys not configured. Operating in standalone PostGIS GeoJSON mode.")

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    def upload_to_storage(self, filename: str, file_bytes: bytes, content_type: str = "image/png") -> str:
        """Upload an orthophoto file to the Supabase Storage 'cadastral-imagery' bucket."""
        if not self._client:
            return f"local://storage/{filename}"

        try:
            res = self._client.storage.from_(SUPABASE_STORAGE_BUCKET).upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            # Retrieve public URL
            public_url = self._client.storage.from_(SUPABASE_STORAGE_BUCKET).get_public_url(filename)
            return public_url
        except Exception as e:
            print(f"[REIGNGRID] Supabase Storage upload error: {e}")
            return f"local://storage/{filename}"

    def get_parcels(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all cadastral parcels from Supabase PostGIS table."""
        if not self._client:
            return None
        try:
            res = self._client.table("parcels").select("*").execute()
            return res.data
        except Exception as e:
            print(f"[REIGNGRID] Supabase fetch error: {e}")
            return None

    def save_ai_detection(self, parcel_id: str, detected_geom: Dict[str, Any], iou_score: float, conflict_with: Optional[str], encroachment_sqft: float):
        """Save AI detected boundary polygon into Supabase 'ai_detections' table."""
        if not self._client:
            return
        try:
            self._client.table("ai_detections").upsert({
                "parcel_id": parcel_id,
                "iou_score": iou_score,
                "conflict_with": conflict_with,
                "encroachment_sqft": encroachment_sqft,
            }).execute()
        except Exception as e:
            print(f"[REIGNGRID] Supabase AI detection insert error: {e}")
            return None

# Global service singleton
supabase_service = SupabaseService()
