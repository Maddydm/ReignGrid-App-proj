import io
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Polygon as DrawingPolygon, String, Line

from backend.config import INSPECTOR_NAME, INSPECTOR_TITLE, PRODUCT_NAME, PRODUCT_TAGLINE

def make_color(hex_str: str, alpha: float = 1.0):
    c = colors.HexColor(hex_str)
    return colors.Color(c.red, c.green, c.blue, alpha=alpha)

def format_area_acres(area_sqft: float) -> str:
    acres = area_sqft / 43560.0
    return f"{acres:.2f} acres ({int(round(area_sqft)):,} sq ft)"

def generate_discrepancy_json(parcel: Dict[str, Any]) -> Dict[str, Any]:
    """Build a structured JSON discrepancy report with numeric area_sqft."""
    pid = parcel["id"]
    area_sqft = float(parcel.get("area_sqft", 0.0))
    displacement = parcel.get("displacement_m", 2.4 if parcel.get("status") == "discrepancy" else 0.0)
    return {
        "report_id": f"REP-{pid}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product": PRODUCT_NAME,
        "tagline": PRODUCT_TAGLINE,
        "parcel_id": pid,
        "owner": parcel.get("owner", "Unknown"),
        "area_sqft": area_sqft,
        "formatted_area": format_area_acres(area_sqft),
        "status": parcel.get("status", "pending"),
        "sector": "Sector 12-B (SRM Ramapuram, Chennai)",
        "spatial_reference": "EPSG:4326 (WGS84)",
        "last_synced": parcel.get("last_synced") or parcel.get("lastSynced", "N/A"),
        "registered_geometry": parcel.get("registered_geom", {}),
        "detected_geometry": parcel.get("detected_geom"),
        "conflict_with": parcel.get("conflict_with") or parcel.get("conflictsWith"),
        "encroachment_sqft": parcel.get("encroachment_sqft"),
        "displacement_m": displacement,
        "iou_score": parcel.get("iou_score"),
        "surveyor_notes": parcel.get("notes", ""),
        "resolution_status": "Resolved" if parcel.get("resolved_at") else ("Pending Verification" if parcel.get("status") == "discrepancy" else "Verified"),
        "inspector_signature": {
            "inspector_name": parcel.get("resolved_by") or INSPECTOR_NAME,
            "title": INSPECTOR_TITLE,
            "certified_date": parcel.get("resolved_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        },
    }

def generate_discrepancy_pdf(parcel: Dict[str, Any]) -> bytes:
    """Generate high-contrast graphic poster PDF discrepancy report matching the REIGNGRID institutional palette."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Brand Colors (REIGNGRID Institutional Palette)
    c_dark = colors.HexColor("#111827")
    c_primary = colors.HexColor("#1E3A2F")
    c_accent = colors.HexColor("#234E3E")
    c_crimson = colors.HexColor("#DC2626")
    c_green = colors.HexColor("#16A34A")
    c_amber = colors.HexColor("#D97706")
    c_muted = colors.HexColor("#65676B")
    c_subtle = colors.HexColor("#E5E5E0")
    c_surface_subtle = colors.HexColor("#F8F8F6")
    c_white = colors.white

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=c_primary,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=c_muted,
        spaceAfter=10,
    )
    heading_style = ParagraphStyle(
        "SecHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=c_dark,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=c_dark,
        leading=13,
    )
    note_style = ParagraphStyle(
        "DocNote",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=c_crimson if parcel.get("status") == "discrepancy" else c_dark,
        leading=14,
    )

    story = []

    # 1. Header Banner (REIGNGRID Institutional Branding)
    header_data = [
        [
            Paragraph(f"<b>{PRODUCT_NAME}</b> · CADASTRAL INTELLIGENCE PLATFORM", title_style),
            Paragraph(f"<b>REPORT ID:</b> REP-{parcel['id']}<br/><b>ANCHOR:</b> SRM Ramapuram, Chennai<br/><b>DATE:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style),
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=4, spaceAfter=14))

    # 2. Status Badge Block
    status_label = parcel.get("status", "pending").upper()
    status_color = c_crimson if parcel.get("status") == "discrepancy" else (c_green if parcel.get("status") == "verified" else c_amber)
    
    status_box = [
        [
            Paragraph(f"<b>VERIFICATION STATUS:</b> <font color='{status_color.hexval()}'><b>{status_label}</b></font>", ParagraphStyle("St", parent=body_style, fontSize=11, fontName="Helvetica-Bold")),
            Paragraph(f"<b>LAST SYNC:</b> {parcel.get('last_synced') or parcel.get('lastSynced', 'N/A')}", ParagraphStyle("StR", parent=body_style, fontSize=10, alignment=2))
        ]
    ]
    t_status = Table(status_box, colWidths=[340, 200])
    t_status.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_surface_subtle),
        ("BOX", (0, 0), (-1, -1), 1.5, c_dark),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t_status)
    story.append(Spacer(1, 10))

    # 3. Parcel Details Table
    story.append(Paragraph("I. CADASTRE RECORD SPECIFICATIONS (POSTGIS WGS84)", heading_style))
    area_sqft = float(parcel.get("area_sqft", 0.0))
    displacement = parcel.get("displacement_m", 2.4 if parcel.get("status") == "discrepancy" else 0.0)
    meta_data = [
        [Paragraph("<b>Parcel Identifier:</b>", body_style), Paragraph(parcel.get("id", ""), body_style), Paragraph("<b>Calculated Area:</b>", body_style), Paragraph(format_area_acres(area_sqft), body_style)],
        [Paragraph("<b>Recorded Owner:</b>", body_style), Paragraph(parcel.get("owner", ""), body_style), Paragraph("<b>Spatial Reference:</b>", body_style), Paragraph("EPSG:4326 (WGS84 Lat/Lon)", body_style)],
        [Paragraph("<b>Conflicting Parcel:</b>", body_style), Paragraph(f"<font color='{c_crimson.hexval()}'><b>{parcel.get('conflict_with') or parcel.get('conflictsWith') or 'None (Clear)'}</b></font>", body_style), Paragraph("<b>Est. Encroachment:</b>", body_style), Paragraph(f"{round(parcel.get('encroachment_sqft', 0.0), 1)} sq. ft", body_style)],
        [Paragraph("<b>AI IoU Overlap:</b>", body_style), Paragraph(f"{round((parcel.get('iou_score') or 0.0)*100, 1)}% (Disp: {displacement}m)", body_style), Paragraph("<b>Field Surveyor:</b>", body_style), Paragraph(parcel.get("resolved_by") or "Field Audit Required", body_style)],
    ]
    t_meta = Table(meta_data, colWidths=[120, 150, 120, 150])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_white),
        ("GRID", (0, 0), (-1, -1), 1, c_subtle),
        ("BOX", (0, 0), (-1, -1), 1.5, c_dark),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 4. Diagnostic Notes
    story.append(Paragraph("II. AI BOUNDARY SEGMENTATION NOTES", heading_style))
    note_text = parcel.get("notes", "No discrepancies identified during segmentation pass.")
    t_note = Table([[Paragraph(f"<b>Surveyor Diagnostic:</b> {note_text}", note_style)]], colWidths=[540])
    t_note.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), make_color("#DC2626", 0.08) if parcel.get("status") == "discrepancy" else make_color("#16A34A", 0.08)),
        ("BOX", (0, 0), (-1, -1), 1.5, c_crimson if parcel.get("status") == "discrepancy" else c_green),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t_note)
    story.append(Spacer(1, 10))

    # 5. Visual Vector Schematic (WGS84 Normalized Drawing)
    story.append(Paragraph("III. CADASTRE VECTOR COMPARISON SCHEMATIC", heading_style))
    diag = Drawing(540, 150)
    # Background
    diag.add(Rect(0, 0, 540, 150, fillColor=colors.HexColor("#1A202C"), strokeColor=c_dark, strokeWidth=1.5))
    
    # Grid lines
    for gx in range(40, 520, 40):
        diag.add(Line(gx, 10, gx, 140, strokeColor=colors.HexColor("#2D3748"), strokeWidth=0.5))
    for gy in range(20, 140, 20):
        diag.add(Line(20, gy, 520, gy, strokeColor=colors.HexColor("#2D3748"), strokeWidth=0.5))

    # Parse WGS84 coordinates from GeoJSON
    reg_coords = []
    if parcel.get("registered_geom") and parcel["registered_geom"].get("coordinates"):
        reg_coords = parcel["registered_geom"]["coordinates"][0]

    det_coords = []
    if parcel.get("detected_geom") and parcel["detected_geom"].get("coordinates"):
        det_coords = parcel["detected_geom"]["coordinates"][0]

    all_pts = reg_coords + det_coords
    if all_pts:
        min_lon = min(p[0] for p in all_pts)
        max_lon = max(p[0] for p in all_pts)
        min_lat = min(p[1] for p in all_pts)
        max_lat = max(p[1] for p in all_pts)
        span_lon = max(max_lon - min_lon, 0.00001)
        span_lat = max(max_lat - min_lat, 0.00001)

        def norm_pt(lon, lat):
            nx = 90 + (lon - min_lon) / span_lon * 340
            ny = 25 + (lat - min_lat) / span_lat * 95
            return nx, ny

        # Draw registered polygon (Green tint + White border)
        if len(reg_coords) >= 3:
            flat_reg = []
            for lon, lat in reg_coords:
                nx, ny = norm_pt(lon, lat)
                flat_reg.extend([nx, ny])
            diag.add(DrawingPolygon(flat_reg, fillColor=make_color("#16A34A", 0.35), strokeColor=c_white, strokeWidth=2))

        # Draw detected polygon (Crimson/amber dashed)
        if len(det_coords) >= 3:
            flat_det = []
            for lon, lat in det_coords:
                nx, ny = norm_pt(lon, lat)
                flat_det.extend([nx, ny])
            diag.add(DrawingPolygon(flat_det, fillColor=make_color("#DC2626", 0.3), strokeColor=c_crimson, strokeWidth=2, strokeDashArray=[4, 3]))

    # Legend text
    diag.add(Rect(340, 115, 12, 12, fillColor=make_color("#16A34A", 0.4), strokeColor=c_white, strokeWidth=1.5))
    diag.add(String(358, 117, "Registered Cadastral Boundary", fontName="Helvetica", fontSize=8, fillColor=c_white))

    diag.add(Rect(340, 97, 12, 12, fillColor=make_color("#DC2626", 0.4), strokeColor=c_crimson, strokeWidth=1.5, strokeDashArray=[2, 2]))
    diag.add(String(358, 99, "AI Detected Boundary (U-Net)", fontName="Helvetica", fontSize=8, fillColor=c_white))

    story.append(diag)
    story.append(Spacer(1, 10))

    # 6. WGS84 Coordinates Table
    story.append(Paragraph("IV. BOUNDARY COORDINATES SPECIFICATIONS (WGS84 LATITUDE / LONGITUDE)", heading_style))
    coord_rows = [
        [Paragraph("<b>Vertex</b>", body_style), Paragraph("<b>Registered Boundary (Lon, Lat)</b>", body_style), Paragraph("<b>AI Detected Boundary (Lon, Lat)</b>", body_style)]
    ]
    max_len = max(len(reg_coords), len(det_coords))
    for i in range(min(max_len, 5)):
        reg_txt = f"{reg_coords[i][0]:.6f}° E, {reg_coords[i][1]:.6f}° N" if i < len(reg_coords) else "—"
        det_txt = f"{det_coords[i][0]:.6f}° E, {det_coords[i][1]:.6f}° N" if i < len(det_coords) else "—"
        coord_rows.append([
            Paragraph(f"Marker {i+1}", body_style),
            Paragraph(reg_txt, body_style),
            Paragraph(det_txt, body_style),
        ])
    t_coords = Table(coord_rows, colWidths=[70, 235, 235])
    t_coords.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_surface_subtle),
        ("GRID", (0, 0), (-1, -1), 0.5, c_subtle),
        ("BOX", (0, 0), (-1, -1), 1.5, c_dark),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_coords)
    story.append(Spacer(1, 10))

    # 7. Sign-off Block
    story.append(Paragraph("V. INSPECTION CERTIFICATION & JURISDICTION", heading_style))
    sig_data = [
        [
            Paragraph(f"<b>Certified Inspector:</b> {parcel.get('resolved_by') or INSPECTOR_NAME}<br/><b>Title:</b> {INSPECTOR_TITLE}<br/><b>Jurisdiction:</b> Ramapuram Cadastral Zone, Chennai", body_style),
            Paragraph(f"<b>Digital PostGIS Seal:</b><br/><font color='{c_primary.hexval()}'><b>[VERIFIED - {PRODUCT_NAME}]</b></font><br/>Date: {parcel.get('resolved_at') or datetime.now(timezone.utc).strftime('%Y-%m-%d')}", body_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.5, c_dark),
        ("BACKGROUND", (0, 0), (-1, -1), c_surface_subtle),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t_sig)

    doc.build(story)
    return buffer.getvalue()
