import uvicorn
from backend.database import db

if __name__ == "__main__":
    print("=" * 70)
    print(" REIGNGRID — Geospatial Intelligence for the Physical World")
    print("=" * 70)
    print(" Geographic Anchor: SRM Ramapuram, Chennai (13.033° N, 80.180° E)")
    print(" Basemap: Esri World Imagery (MapLibre GL JS)")
    print(" Design System: Warm Institutional Palette (#F8F8F6, #1E3A2F, #111827)")
    print(f" Database: {len(db.get_all_parcels())} cadastral parcels loaded with PostGIS WGS84 GeoJSON.")
    print(" Web Application: http://127.0.0.1:8000")
    print(" Interactive API Docs: http://127.0.0.1:8000/docs")
    print(" Inspector Credentials: inspector@reigngrid.gov / inspector123")
    print("=" * 70)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
