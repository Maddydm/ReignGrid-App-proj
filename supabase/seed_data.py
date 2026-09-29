import os
import json
from pathlib import Path
from shapely.geometry import Polygon, mapping

# Base coordinate anchor: SRM Institute of Science & Technology, Ramapuram, Chennai
# Latitude: 13.0332° N, Longitude: 80.1805° E
BASE_LON = 80.18050
BASE_LAT = 13.03320

# Conversion constants
SQFT_PER_ACRE = 43560.0

# 10 Cadastral Parcels anchored over SRM Ramapuram
# Layout matches the 5x2 sector grid:
# Row 1 (North): PCL-1042, PCL-1043, PCL-1044, PCL-1045, PCL-1046
# Row 2 (South): PCL-1047, PCL-1048, PCL-1049, PCL-1050, PCL-1051

def make_wgs84_polygon(col_idx: int, row_idx: int, shift_x: float = 0.0, shift_y: float = 0.0) -> list:
    """Generate WGS84 coordinates for a parcel cell with optional boundary shift."""
    dx = 0.00042  # ~45.5 meters longitude
    dy = 0.00038  # ~42.0 meters latitude
    gap = 0.00002 # ~2.2 meters survey access boundary

    x0 = BASE_LON + col_idx * (dx + gap) + shift_x
    y0 = BASE_LAT - row_idx * (dy + gap) + shift_y
    x1 = x0 + dx
    y1 = y0 - dy

    # Return GeoJSON closed ring: [ [lon, lat], [lon, lat], ... ]
    return [
        [round(x0, 7), round(y0, 7)],
        [round(x1, 7), round(y0, 7)],
        [round(x1, 7), round(y1, 7)],
        [round(x0, 7), round(y1, 7)],
        [round(x0, 7), round(y0, 7)],
    ]

PARCELS_METADATA = [
    {
        "id": "PCL-1042",
        "owner": "Lakshmi Narayanan",
        "acres": 0.51,
        "status": "verified",
        "last_synced": "2024-11-02",
        "notes": "Registered and AI-detected boundaries match within 2.1% tolerance.",
        "col": 0, "row": 0,
        "has_detection": True,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": 0.98,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1043",
        "owner": "S. Kumaravel",
        "acres": 0.44,
        "status": "verified",
        "last_synced": "2024-11-02",
        "notes": "Registered and AI-detected boundaries match within 3.0% tolerance.",
        "col": 1, "row": 0,
        "has_detection": True,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": 0.97,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1044",
        "owner": "Devika Raman",
        "acres": 0.61,
        "status": "discrepancy",
        "last_synced": "2024-11-02",
        "notes": "AI-detected boundary extends ~340 sq. ft east into PCL-1045. Flagged for field verification.",
        "col": 2, "row": 0,
        "has_detection": True,
        "shift_det_x": 0.00008, "shift_det_y": 0.0,  # Extends east into col 3 (PCL-1045)
        "iou_score": 0.81,
        "conflict_with": "PCL-1045",
        "encroachment_sqft": 340.0,
    },
    {
        "id": "PCL-1045",
        "owner": "Arjun Mehta",
        "acres": 0.48,
        "status": "verified",
        "last_synced": "2024-11-02",
        "notes": "Overlapped by an AI-detected extension from PCL-1044. Cadastral boundary itself unchanged.",
        "col": 3, "row": 0,
        "has_detection": True,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": 0.96,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1046",
        "owner": "Priya Sundaram",
        "acres": 0.39,
        "status": "pending",
        "last_synced": "2024-10-18",
        "notes": "High-resolution imagery captured; awaiting AI segmentation pass.",
        "col": 4, "row": 0,
        "has_detection": False,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": None,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1047",
        "owner": "T. Ravichandran",
        "acres": 0.55,
        "status": "verified",
        "last_synced": "2024-11-02",
        "notes": "Registered and AI-detected boundaries match within 1.2% tolerance.",
        "col": 0, "row": 1,
        "has_detection": True,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": 0.99,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1048",
        "owner": "Meena Krishnan",
        "acres": 0.58,
        "status": "discrepancy",
        "last_synced": "2024-11-02",
        "notes": "AI-detected boundary overlaps PCL-1049 by ~210 sq. ft — possible fence encroachment.",
        "col": 1, "row": 1,
        "has_detection": True,
        "shift_det_x": 0.00006, "shift_det_y": 0.0,  # Extends east into col 2 (PCL-1049)
        "iou_score": 0.83,
        "conflict_with": "PCL-1049",
        "encroachment_sqft": 210.0,
    },
    {
        "id": "PCL-1049",
        "owner": "Suresh Babu",
        "acres": 0.47,
        "status": "verified",
        "last_synced": "2024-11-02",
        "notes": "Overlapped by an AI-detected extension from PCL-1048. Cadastral boundary itself unchanged.",
        "col": 2, "row": 1,
        "has_detection": True,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": 0.95,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1050",
        "owner": "Anitha Raghavan",
        "acres": 0.50,
        "status": "verified",
        "last_synced": "2024-11-02",
        "notes": "Registered and AI-detected boundaries match within 2.8% tolerance.",
        "col": 3, "row": 1,
        "has_detection": True,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": 0.97,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1051",
        "owner": "K. Balamurugan",
        "acres": 0.41,
        "status": "pending",
        "last_synced": "2024-10-18",
        "notes": "High-resolution imagery captured; awaiting AI segmentation pass.",
        "col": 4, "row": 1,
        "has_detection": False,
        "shift_det_x": 0.0, "shift_det_y": 0.0,
        "iou_score": None,
        "conflict_with": None,
        "encroachment_sqft": 0.0,
    },
]

def build_geojson_data():
    """Build structured parcel and detection dataset with WGS84 geometries."""
    parcels = []
    detections = []

    for item in PARCELS_METADATA:
        reg_coords = make_wgs84_polygon(item["col"], item["row"])
        area_sqft = round(item["acres"] * SQFT_PER_ACRE, 1)

        parcel_entry = {
            "id": item["id"],
            "owner": item["owner"],
            "area_sqft": area_sqft,
            "status": item["status"],
            "last_synced": item["last_synced"],
            "notes": item["notes"],
            "registered_geom": {
                "type": "Polygon",
                "coordinates": [reg_coords]
            }
        }
        parcels.append(parcel_entry)

        if item["has_detection"]:
            det_coords = make_wgs84_polygon(
                item["col"], item["row"],
                shift_x=item["shift_det_x"],
                shift_y=item["shift_det_y"]
            )
            detection_entry = {
                "parcel_id": item["id"],
                "detected_geom": {
                    "type": "Polygon",
                    "coordinates": [det_coords]
                },
                "iou_score": item["iou_score"],
                "conflict_with": item["conflict_with"],
                "encroachment_sqft": item["encroachment_sqft"]
            }
            detections.append(detection_entry)

    # Sector bounds covering all parcels
    sector_bounds = [
        [round(BASE_LON - 0.0001, 7), round(BASE_LAT + 0.0001, 7)],
        [round(BASE_LON + 5 * 0.00045 + 0.0001, 7), round(BASE_LAT + 0.0001, 7)],
        [round(BASE_LON + 5 * 0.00045 + 0.0001, 7), round(BASE_LAT - 2 * 0.00041 - 0.0001, 7)],
        [round(BASE_LON - 0.0001, 7), round(BASE_LAT - 2 * 0.00041 - 0.0001, 7)],
        [round(BASE_LON - 0.0001, 7), round(BASE_LAT + 0.0001, 7)],
    ]

    imagery = [
        {
            "id": "img-srm-ramapuram-01",
            "source": "SRM Ramapuram High-Resolution Drone Orthophoto (0.05m GSD)",
            "file_path": "imagery/srm_ramapuram_survey_2024.tif",
            "bounds": {
                "type": "Polygon",
                "coordinates": [sector_bounds]
            }
        }
    ]

    return parcels, detections, imagery

def generate_seed_sql_file():
    """Export complete SQL seed file for Supabase SQL Editor."""
    parcels, detections, imagery = build_geojson_data()
    sql_lines = [
        "-- ============================================================================",
        "-- LandSight PostGIS Seed Data — SRM Ramapuram, Chennai (Sector 12-B)",
        "-- ============================================================================\n",
        "BEGIN;\n",
    ]

    # Insert parcels
    sql_lines.append("-- 1. Insert Registered Cadastral Parcels")
    for p in parcels:
        geom_geojson = json.dumps(p["registered_geom"])
        notes_escaped = p["notes"].replace("'", "''")
        owner_escaped = p["owner"].replace("'", "''")
        sql_lines.append(
            f"INSERT INTO public.parcels (id, owner, area_sqft, status, last_synced, registered_geom, notes) "
            f"VALUES ('{p['id']}', '{owner_escaped}', {p['area_sqft']}, '{p['status']}', '{p['last_synced']}', "
            f"ST_SetSRID(ST_GeomFromGeoJSON('{geom_geojson}'), 4326), '{notes_escaped}') "
            f"ON CONFLICT (id) DO UPDATE SET "
            f"owner = EXCLUDED.owner, area_sqft = EXCLUDED.area_sqft, status = EXCLUDED.status, "
            f"last_synced = EXCLUDED.last_synced, registered_geom = EXCLUDED.registered_geom, notes = EXCLUDED.notes;\n"
        )

    # Insert detections
    sql_lines.append("\n-- 2. Insert AI Detected Boundaries")
    for d in detections:
        geom_geojson = json.dumps(d["detected_geom"])
        conflict_val = f"'{d['conflict_with']}'" if d["conflict_with"] else "NULL"
        iou_val = f"{d['iou_score']}" if d["iou_score"] is not None else "NULL"
        sql_lines.append(
            f"INSERT INTO public.ai_detections (parcel_id, detected_geom, iou_score, conflict_with, encroachment_sqft) "
            f"VALUES ('{d['parcel_id']}', ST_SetSRID(ST_GeomFromGeoJSON('{geom_geojson}'), 4326), {iou_val}, {conflict_val}, {d['encroachment_sqft']});\n"
        )

    # Insert imagery
    sql_lines.append("\n-- 3. Insert Survey Imagery Record")
    for img in imagery:
        geom_geojson = json.dumps(img["bounds"])
        source_escaped = img["source"].replace("'", "''")
        sql_lines.append(
            f"INSERT INTO public.imagery (id, source, file_path, bounds) "
            f"VALUES ('{img['id']}', '{source_escaped}', '{img['file_path']}', ST_SetSRID(ST_GeomFromGeoJSON('{geom_geojson}'), 4326)) "
            f"ON CONFLICT (id) DO UPDATE SET source = EXCLUDED.source, file_path = EXCLUDED.file_path, bounds = EXCLUDED.bounds;\n"
        )

    sql_lines.append("COMMIT;\n")

    out_path = Path(__file__).resolve().parent / "seed_data.sql"
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(sql_lines)
    print(f"Generated seed SQL file at: {out_path}")
    return out_path

def seed_supabase_client():
    """Seed directly via supabase-py client if credentials are configured."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY not set in environment.")
        print("Seed data generated as SQL script instead. Run 'supabase/seed_data.sql' in the Supabase SQL editor.")
        return

    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        parcels, detections, imagery = build_geojson_data()
        
        print(f"Connecting to Supabase at {supabase_url}...")
        for p in parcels:
            supabase.table("parcels").upsert({
                "id": p["id"],
                "owner": p["owner"],
                "area_sqft": p["area_sqft"],
                "status": p["status"],
                "last_synced": p["last_synced"],
                "notes": p["notes"],
            }).execute()
        print(f"Successfully seeded {len(parcels)} parcels to Supabase.")
    except Exception as e:
        print(f"Supabase-py seeding exception: {e}")

if __name__ == "__main__":
    generate_seed_sql_file()
    seed_supabase_client()
