import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "landsight-frontend"
DATA_DIR = BACKEND_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "reports"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "cadastral-imagery")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "reigngrid-cadastral-secret-key-2026")

# Security & Inspector Credentials
INSPECTOR_EMAIL = os.getenv("INSPECTOR_EMAIL", "inspector@reigngrid.gov")
INSPECTOR_PASSWORD = os.getenv("INSPECTOR_PASSWORD", "inspector123")
INSPECTOR_NAME = "Dr. J. Jean Justus"
INSPECTOR_TITLE = "Chief Cadastral Surveyor"

# Legacy email support for test suite compatibility
LEGACY_INSPECTOR_EMAIL = "inspector@landsight.gov"

# JWT & Security
JWT_SECRET_KEY = SUPABASE_JWT_SECRET
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Geographic Anchor: SRM Ramapuram, Chennai
ANCHOR_LON = 80.1805
ANCHOR_LAT = 13.0332
IOU_TOLERANCE_VERIFIED = 0.90
PRODUCT_NAME = "REIGNGRID"
PRODUCT_TAGLINE = "Geospatial Intelligence for the Physical World."
