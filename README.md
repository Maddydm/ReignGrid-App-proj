# REIGNGRID — Geospatial Intelligence for the Physical World

**ReignGrid** is an institutional AI-powered cadastral intelligence platform that compares official land registry records with high-resolution aerial, drone, and satellite imagery to detect:
- Boundary discrepancies & overlaps
- Illegal land encroachments
- Cadastral parcel shifts
- Unauthorized structural annexes
- Temporal ground modifications

---

## 1. Product Identity & Design System

- **Product Name**: `REIGNGRID`
- **Tagline**: *"Geospatial Intelligence for the Physical World."*
- **Aesthetic**: Serious, professional, institutional GIS cadastral software tailored for government land authorities, surveyors, and field inspectors.
- **Color Tokens**:
  - Canvas: Warm off-white / ivory (`#F8F8F6`)
  - Cards & Surfaces: Clean white (`#FFFFFF`) with subtle 1px borders (`#E5E5E0`)
  - Typography: Dark charcoal primary text (`#1C1E21`), muted gray (`#65676B`)
  - Brand Accent: Deep geographic forest green (`#1E3A2F`), dark slate (`#111827`)
  - Status Verified: Forest Green (`#16A34A` / badge `#DCFCE7`)
  - Status Pending / Review: Amber (`#D97706` / badge `#FEF3C7`)
  - Status Discrepancy / Overlap: Crimson (`#DC2626` / badge `#FEE2E2`)
- **Typography**:
  - Body & Headings: `Inter`
  - IDs & Coordinates: `IBM Plex Mono` (`PCL-1044`, `13.0332° N, 80.1805° E`, `0.81 IoU`)

---

## 2. Multi-Screen Architecture (8 Primary Views)

1. **Screen 1: Landing Page (`See what changed on the ground.`)**:
   - Institutional navbar with quick navigation to all modules.
   - High-contrast hero section with realistic satellite preview of SRM Ramapuram cadastral parcels.
   - Dual CTAs: *Launch Command Center* and *Explore Map Intelligence*.
2. **Screen 2: Command Center**:
   - Left institutional sidebar with active inspector status (`Dr. J. Jean Justus`).
   - Top 5 KPI cards pulling directly from `/api/dashboard/summary`:
     - `1,248 Total Parcels`
     - `1,116 Verified Boundaries`
     - `84 Needs Review`
     - `48 Discrepancies`
     - `642.8 ac Monitored Area`
   - Central MapLibre GL JS satellite map with Esri World Imagery tiles and floating legend bar.
   - Right **Parcel Intelligence** panel featuring active parcel metrics, surveyor diagnostic notes, and working action buttons.
3. **Screen 3: Map Intelligence (Full-Bleed GIS Workspace)**:
   - Floating layer toggles (Satellite basemap, Registered cadastre, AI boundaries, Encroachment highlights).
   - Real-time mouse coordinate tracker (WGS84 Lat/Lon).
   - AI overlay opacity slider.
4. **Screen 4: Parcel Comparison Modal (Dual Vector View)**:
   - Side-by-side comparison of **Registered Cadastral Record** vs **AI-Derived Boundary (Drone Ortho)**.
   - IoU score (`0.81`), centroid displacement (`2.4 m East`), affected area (`340 sq ft`), dispute risk (`HIGH`).
5. **Screen 5: AI Processing (7-Stage Pipeline Stepper)**:
   - 01 Ingestion → 02 Orthorectification & CLAHE → 03 U-Net Segmentation → 04 Vectorization → 05 Cadastral Cross-Reference → 06 IoU Calculation → 07 Database Sync.
   - Real-time execution timer and live pipeline dispatch.
6. **Screen 6: Discrepancy Center**:
   - Filter tabs: `All (48)`, `High Priority (18)`, `Medium (22)`, `Low (8)`, `Unresolved (42)`, `Resolved (6)`.
   - Comprehensive data table with sorting, search, and action triggers (*Inspect*, *Assign*, *Report*).
7. **Screen 7: Field Verification Workflow**:
   - 5-stage stepper: `AI Detection` → `Inspector Review` → `Field Survey` → `Evidence` → `Resolution`.
   - Active survey assignment details, GPS RTK coordinates, evidence photo upload dropzone with thumbnail preview, field surveyor observation notes, and *Submit Verification* action.
8. **Screen 8: Official Report Preview & Export**:
   - High-contrast official Cadastral Boundary Verification Report certificate.
   - Direct download links for **PDF Report** (via ReportLab engine) and **JSON Data Export**.

---

## 3. Technology Stack

- **Backend**: FastAPI (Python 3.10+), Pydantic v2, Uvicorn
- **Spatial & AI Pipeline**: PyTorch (U-Net), Shapely, OpenCV, Rasterio
- **Database & Storage**: PostGIS (WGS84 EPSG:4326), Supabase Storage client, local JSON fallback (`reigngrid_db.json`)
- **PDF Generation**: ReportLab
- **Frontend**: Vanilla HTML5, CSS3 Custom Properties, MapLibre GL JS v4, Lucide Icons

---

## 4. Getting Started

### Local Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application**:
   ```bash
   python run.py
   ```

3. **Open the browser**:
   - Web Platform: `http://127.0.0.1:8000`
   - Interactive API Docs: `http://127.0.0.1:8000/docs`

4. **Default Inspector Credentials**:
   - Email / Username: `inspector@reigngrid.gov`
   - Password: `inspector123`

### Run Backend Tests

```bash
python tests/test_backend.py
```
