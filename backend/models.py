from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ParcelBase(BaseModel):
    id: str = Field(..., example="PCL-1044")
    owner: str = Field(..., example="Devika Raman")
    area_sqft: float = Field(..., example=26571.6) # Raw numeric square footage
    status: str = Field(..., example="discrepancy") # 'verified' | 'discrepancy' | 'pending'
    last_synced: str = Field(..., example="2024-11-02")
    notes: Optional[str] = Field(None, example="AI-detected boundary extends ~340 sq. ft into PCL-1045.")
    registered_geom: Dict[str, Any] = Field(..., example={"type": "Polygon", "coordinates": [[[80.18138, 13.0332], ...]]})
    detected_geom: Optional[Dict[str, Any]] = None
    conflict_with: Optional[str] = Field(None, example="PCL-1045")
    iou_score: Optional[float] = Field(None, example=0.81)
    encroachment_sqft: Optional[float] = Field(None, example=340.0)
    displacement_m: Optional[float] = Field(2.4, example=2.4)
    priority: Optional[str] = Field("HIGH", example="HIGH")
    
    # Aliases for frontend convenience
    @property
    def conflictsWith(self) -> Optional[str]:
        return self.conflict_with

    @property
    def lastSynced(self) -> str:
        return self.last_synced

class ParcelResponse(BaseModel):
    id: str
    owner: str
    area_sqft: float
    status: str
    last_synced: str
    lastSynced: Optional[str] = None
    notes: Optional[str] = None
    registered_geom: Dict[str, Any]
    detected_geom: Optional[Dict[str, Any]] = None
    conflict_with: Optional[str] = None
    conflictsWith: Optional[str] = None
    iou_score: Optional[float] = None
    encroachment_sqft: Optional[float] = None
    displacement_m: Optional[float] = None
    priority: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None

class ParcelDetailResponse(ParcelResponse):
    geometry_type: str = "Polygon"
    spatial_reference: str = "WGS84 (EPSG:4326) · SRM Ramapuram Anchor"
    discrepancy_details: Optional[Dict[str, Any]] = None

class ImageryRecord(BaseModel):
    imagery_id: str
    area_name: str
    filename: str
    source_type: str # 'file' | 'path' | 'url'
    file_path: Optional[str] = None
    source_url: Optional[str] = None
    uploaded_at: str
    status: str # 'uploaded' | 'processed' | 'error'
    resolution_m_per_px: float = 0.05
    description: Optional[str] = None
    bounds: Optional[Dict[str, Any]] = None

class ProcessResult(BaseModel):
    imagery_id: str
    area_name: str
    status: str
    parcels_processed: int
    discrepancies_detected: int
    verified_parcels: int
    pending_parcels: int
    processing_time_seconds: float
    pipeline_stages: List[Dict[str, Any]]
    completed_at: str

class LoginRequest(BaseModel):
    username: str = Field(..., example="inspector@reigngrid.gov")
    password: str = Field(..., example="inspector123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "inspector"
    user_name: str
    user_email: str
    expires_in: int

class UserProfile(BaseModel):
    email: str
    name: str
    role: str
    title: str

class DiscrepancyResolutionRequest(BaseModel):
    resolution_notes: str = Field(..., example="Field survey completed. Boundary dispute resolved.")

class DiscrepancyReportJSON(BaseModel):
    report_id: str
    generated_at: str
    parcel_id: str
    owner: str
    area_sqft: float
    formatted_area: str
    status: str
    sector: str
    last_synced: str
    registered_geometry: Dict[str, Any]
    detected_geometry: Optional[Dict[str, Any]]
    conflict_with: Optional[str]
    encroachment_sqft: Optional[float]
    displacement_m: Optional[float]
    iou_score: Optional[float]
    surveyor_notes: str
    resolution_status: str
    inspector_signature: Dict[str, Any]

# --------------------------------------------------------------------------
# REIGNGRID Domain Models for UI Reference Alignment
# --------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    total_parcels: int = 1248
    verified_parcels: int = 1116
    needs_review: int = 84
    discrepancies: int = 48
    monitored_acres: float = 642.8
    sector: str = "Sector 12-B"
    location: str = "SRM Ramapuram, Chennai"
    gsd_m: float = 0.05
    last_sync: str = "2024-11-02"
    ai_engine_status: str = "ONLINE"
    indexed_parcels_count: int = 1248

class DiscrepancyItem(BaseModel):
    id: str
    parcel_id: str
    owner: str
    conflict_with: Optional[str] = None
    encroachment_sqft: float = 0.0
    displacement_m: float = 0.0
    iou_score: float = 0.0
    priority: str # 'HIGH' | 'MEDIUM' | 'LOW'
    status: str # 'Unresolved' | 'Assigned' | 'Resolved'
    assigned_inspector: Optional[str] = None
    sector: str = "Sector 12-B"
    flagged_date: str
    notes: Optional[str] = None

class AssignSurveyRequest(BaseModel):
    inspector_name: str = Field(..., example="Dr. J. Jean Justus")
    priority: str = Field("HIGH", example="HIGH")
    due_date: str = Field("2024-11-10", example="2024-11-10")
    survey_notes: Optional[str] = Field(None, example="Verify eastern fence line adjacent to PCL-1045.")

class FieldVerificationItem(BaseModel):
    id: str
    parcel_id: str
    conflict_with: Optional[str] = None
    owner: str
    sector: str = "Sector 12-B"
    current_step: int = 3 # 1 to 5
    step_names: List[str] = [
        "AI Detection",
        "Inspector Review",
        "Field Survey",
        "Evidence Collection",
        "Official Resolution"
    ]
    priority: str = "HIGH"
    assigned_inspector: str = "Dr. J. Jean Justus"
    scheduled_date: str = "2024-11-04"
    coordinates: str = "13.03324° N, 80.18142° E"
    encroachment_sqft: float = 340.0
    displacement_m: float = 2.4
    evidence_photos: List[str] = []
    field_notes: Optional[str] = None
    status: str = "In Progress" # 'Pending' | 'In Progress' | 'Evidence Collected' | 'Resolved'
    resolved_at: Optional[str] = None

class SubmitVerificationRequest(BaseModel):
    field_notes: str = Field(..., example="Ground marker stones verified. Fence encroachment of 340 sq ft confirmed.")
    evidence_photo_url: Optional[str] = Field(None, example="evidence_marker_1044.jpg")
    resolution_action: str = Field("resolve_verified", example="resolve_verified") # 'resolve_verified' | 'confirm_encroachment'

class ActivityLogItem(BaseModel):
    id: str
    timestamp: str
    event_type: str # 'AI_DETECTION' | 'SURVEY_ASSIGNED' | 'EVIDENCE_UPLOADED' | 'DISCREPANCY_RESOLVED' | 'IMAGERY_INGESTED'
    title: str
    description: str
    parcel_id: Optional[str] = None
    actor: str = "System"
