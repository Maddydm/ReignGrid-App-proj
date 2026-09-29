import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from backend.config import UPLOADS_DIR

INITIAL_PARCELS = [
    {
        "id": "PCL-1042",
        "owner": "Lakshmi Narayanan",
        "area": "0.51 acres",
        "status": "verified",
        "lastSynced": "2024-11-02",
        "note": "Registered and AI-detected boundaries match within tolerance.",
        "registered": "80,140 260,130 270,300 90,310",
        "detected": "80,140 260,130 270,300 90,310",
        "conflictsWith": None,
        "iou_score": 0.98,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1043",
        "owner": "S. Kumaravel",
        "area": "0.44 acres",
        "status": "verified",
        "lastSynced": "2024-11-02",
        "note": "Registered and AI-detected boundaries match within tolerance.",
        "registered": "270,130 460,140 450,300 270,300",
        "detected": "270,130 460,140 450,300 270,300",
        "conflictsWith": None,
        "iou_score": 0.97,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1044",
        "owner": "Devika Raman",
        "area": "0.61 acres",
        "status": "discrepancy",
        "lastSynced": "2024-11-02",
        "note": "AI-detected boundary extends ~340 sq. ft into PCL-1045. Flagged for field verification.",
        "registered": "460,140 640,150 630,300 450,300",
        "detected": "500,150 680,160 670,300 490,300",
        "conflictsWith": "PCL-1045",
        "iou_score": 0.81,
        "encroachment_sqft": 340.0,
    },
    {
        "id": "PCL-1045",
        "owner": "Arjun Mehta",
        "area": "0.48 acres",
        "status": "verified",
        "lastSynced": "2024-11-02",
        "note": "Overlapped by an AI-detected extension from PCL-1044. Boundary itself unchanged.",
        "registered": "640,150 820,160 810,300 630,300",
        "detected": "640,150 820,160 810,300 630,300",
        "conflictsWith": None,
        "iou_score": 0.96,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1046",
        "owner": "Priya Sundaram",
        "area": "0.39 acres",
        "status": "pending",
        "lastSynced": "2024-10-18",
        "note": "Imagery captured; awaiting AI segmentation pass.",
        "registered": "820,160 940,165 935,300 810,300",
        "detected": None,
        "conflictsWith": None,
        "iou_score": None,
        "encroachment_sqft": None,
    },
    {
        "id": "PCL-1047",
        "owner": "T. Ravichandran",
        "area": "0.55 acres",
        "status": "verified",
        "lastSynced": "2024-11-02",
        "note": "Registered and AI-detected boundaries match within tolerance.",
        "registered": "80,320 270,310 280,480 90,490",
        "detected": "80,320 270,310 280,480 90,490",
        "conflictsWith": None,
        "iou_score": 0.99,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1048",
        "owner": "Meena Krishnan",
        "area": "0.58 acres",
        "status": "discrepancy",
        "lastSynced": "2024-11-02",
        "note": "AI-detected boundary overlaps PCL-1049 by an estimated 210 sq. ft — possible encroachment.",
        "registered": "280,310 460,320 450,480 270,480",
        "detected": "320,320 500,330 490,480 310,480",
        "conflictsWith": "PCL-1049",
        "iou_score": 0.83,
        "encroachment_sqft": 210.0,
    },
    {
        "id": "PCL-1049",
        "owner": "Suresh Babu",
        "area": "0.47 acres",
        "status": "verified",
        "lastSynced": "2024-11-02",
        "note": "Overlapped by an AI-detected extension from PCL-1048. Boundary itself unchanged.",
        "registered": "460,320 640,330 630,480 450,480",
        "detected": "460,320 640,330 630,480 450,480",
        "conflictsWith": None,
        "iou_score": 0.95,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1050",
        "owner": "Anitha Raghavan",
        "area": "0.50 acres",
        "status": "verified",
        "lastSynced": "2024-11-02",
        "note": "Registered and AI-detected boundaries match within tolerance.",
        "registered": "640,330 820,340 810,480 630,480",
        "detected": "640,330 820,340 810,480 630,480",
        "conflictsWith": None,
        "iou_score": 0.97,
        "encroachment_sqft": 0.0,
    },
    {
        "id": "PCL-1051",
        "owner": "K. Balamurugan",
        "area": "0.41 acres",
        "status": "pending",
        "lastSynced": "2024-10-18",
        "note": "Imagery captured; awaiting AI segmentation pass.",
        "registered": "820,340 940,345 935,480 810,480",
        "detected": None,
        "conflictsWith": None,
        "iou_score": None,
        "encroachment_sqft": None,
    },
]

def parse_points(points_str: str):
    """Parse 'x1,y1 x2,y2' string into list of [x, y] coordinates."""
    coords = []
    for pair in points_str.strip().split():
        x, y = pair.split(",")
        coords.append([float(x), float(y)])
    return coords

def generate_sample_orthophoto() -> str:
    """Generate a high-detail synthetic drone orthophoto representing Sector 12-B."""
    img_path = UPLOADS_DIR / "sector12b_drone_ortho.png"
    if img_path.exists():
        return str(img_path)

    width, height = 1000, 560
    
    # Base terrain layer with agricultural / soil textures
    np.random.seed(42)
    base_color = np.array([45, 62, 50], dtype=np.uint8) # Dark field green
    noise = np.random.randint(-15, 15, (height, width, 3), dtype=np.int16)
    img_arr = np.clip(base_color + noise, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(img_arr)
    draw = ImageDraw.Draw(img)

    # Draw agricultural rows / subtle terrain gradient
    for y in range(0, height, 14):
        draw.line([(0, y), (width, y)], fill=(40, 55, 45), width=1)

    # Draw cadastral road / survey access path
    road_points = [(0, 80), (1000, 70)]
    draw.line(road_points, fill=(110, 105, 90), width=14)
    draw.line([(0, 305), (1000, 305)], fill=(90, 85, 75), width=8)

    # Draw field parcels with hedge/fence boundaries
    for p in INITIAL_PARCELS:
        # Use detected if available, otherwise registered
        pts_str = p.get("detected") or p.get("registered")
        poly = [tuple(pt) for pt in parse_points(pts_str)]
        
        # Crop variations inside parcel
        fill_tint = (50 + (hash(p["id"]) % 25), 70 + (hash(p["owner"]) % 20), 55)
        draw.polygon(poly, fill=fill_tint)
        
        # Parcel hedgerow / boundary line
        draw.polygon(poly, outline=(140, 130, 100), width=3)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.save(img_path)
    return str(img_path)
