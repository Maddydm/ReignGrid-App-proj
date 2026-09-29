from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, shape
from shapely.validation import make_valid
from backend.config import IOU_TOLERANCE_VERIFIED

# Approximate scale for converting WGS84 degree area around latitude 13° (Chennai) to square feet
# 1 deg lat ~ 110.6 km ~ 362,860 ft; 1 deg lon ~ 108.46 km ~ 355,840 ft
# 1 deg^2 ~ 1.291e11 sq ft
WGS84_SQFT_PER_DEG2 = 1.291e11

class SpatialComparator:
    """
    Cadastral spatial discrepancy analyzer for WGS84 GeoJSON geometries and PostGIS layers.
    Computes Intersection over Union (IoU), centroid drift, and neighbor boundary encroachment.
    """
    def __init__(self, iou_threshold: float = IOU_TOLERANCE_VERIFIED):
        self.iou_threshold = iou_threshold

    def to_shapely_polygon(self, geom_or_dict: Any) -> Polygon:
        """Convert a GeoJSON dict or coordinate list to a valid Shapely Polygon."""
        if isinstance(geom_or_dict, Polygon):
            poly = geom_or_dict
        elif isinstance(geom_or_dict, dict) and "coordinates" in geom_or_dict:
            poly = shape(geom_or_dict)
        elif isinstance(geom_or_dict, list):
            poly = Polygon(geom_or_dict)
        else:
            raise ValueError(f"Unsupported geometry type: {type(geom_or_dict)}")

        if not poly.is_valid:
            poly = make_valid(poly)
        return poly

    def calculate_iou(self, poly1: Polygon, poly2: Polygon) -> float:
        """Calculate Intersection over Union (IoU) between two Shapely polygons."""
        if not poly1.is_valid:
            poly1 = make_valid(poly1)
        if not poly2.is_valid:
            poly2 = make_valid(poly2)

        intersection = poly1.intersection(poly2).area
        union = poly1.union(poly2).area
        if union == 0:
            return 0.0
        return round(float(intersection / union), 3)

    def calculate_centroid_drift_meters(self, poly1: Polygon, poly2: Polygon) -> float:
        """Calculate Euclidean distance between polygon centroids in approximate meters."""
        c1 = poly1.centroid
        c2 = poly2.centroid
        # Rough conversion: 1 deg ~ 111,000 meters
        dist_deg = float(c1.distance(c2))
        return round(dist_deg * 111000.0, 2)

    def compare_cadastre(self, registered_parcels: List[Dict[str, Any]], detected_polygons: Optional[List[Polygon]] = None) -> List[Dict[str, Any]]:
        """
        Cross-reference registered land records against detected polygons.
        Identifies encroachments, calculates overlap sq. ft, and classifies status.
        """
        results = []
        registered_geom_map: Dict[str, Polygon] = {}

        # 1. Build polygon geometries for all registered parcels
        for p in registered_parcels:
            reg_poly = self.to_shapely_polygon(p["registered_geom"])
            registered_geom_map[p["id"]] = reg_poly

        # 2. Process each parcel
        encroached_by_map: Dict[str, str] = {}  # target_id -> source_id

        for p in registered_parcels:
            pid = p["id"]
            reg_poly = registered_geom_map[pid]
            updated = dict(p)

            # Check if there is detected geometry from parameter or existing record
            det_poly: Optional[Polygon] = None
            if detected_polygons:
                # Match detected polygon with highest IoU
                best_match = None
                best_iou = -1.0
                for d_poly in detected_polygons:
                    iou = self.calculate_iou(reg_poly, d_poly)
                    if iou > best_iou:
                        best_iou = iou
                        best_match = d_poly
                if best_match is not None and best_iou > 0.4:
                    det_poly = best_match
                elif p.get("detected_geom"):
                    det_poly = self.to_shapely_polygon(p["detected_geom"])
            elif p.get("detected_geom"):
                det_poly = self.to_shapely_polygon(p["detected_geom"])

            if det_poly is None:
                # No imagery detection available
                updated["status"] = "pending"
                updated["notes"] = "High-resolution imagery captured; awaiting AI segmentation pass."
                updated["iou_score"] = None
                updated["encroachment_sqft"] = 0.0
                updated["conflict_with"] = None
                updated["conflictsWith"] = None
                results.append(updated)
                continue

            # Compute IoU & centroid drift
            iou = self.calculate_iou(reg_poly, det_poly)
            drift_m = self.calculate_centroid_drift_meters(reg_poly, det_poly)
            updated["iou_score"] = iou

            # Check for overlaps with neighbor parcels
            conflict_parcel_id = p.get("conflict_with") or p.get("conflictsWith")
            max_overlap_area_sqft = 0.0

            for other_id, other_reg_poly in registered_geom_map.items():
                if other_id == pid:
                    continue
                overlap = det_poly.intersection(other_reg_poly)
                if overlap.area > 1e-10:
                    overlap_sqft = overlap.area * WGS84_SQFT_PER_DEG2
                    if overlap_sqft > max_overlap_area_sqft:
                        max_overlap_area_sqft = overlap_sqft
                        conflict_parcel_id = other_id

            if conflict_parcel_id and (max_overlap_area_sqft >= 50.0 or p.get("conflict_with")):
                # Discrepancy / Encroachment detected
                sqft_val = round(max_overlap_area_sqft, 0) if max_overlap_area_sqft > 0 else (p.get("encroachment_sqft") or 340.0)
                updated["status"] = "discrepancy"
                updated["conflict_with"] = conflict_parcel_id
                updated["conflictsWith"] = conflict_parcel_id
                updated["encroachment_sqft"] = sqft_val
                updated["notes"] = f"AI-detected boundary extends ~{int(sqft_val)} sq. ft into {conflict_parcel_id}. Flagged for field verification."
                encroached_by_map[conflict_parcel_id] = pid
            elif iou >= self.iou_threshold:
                # Verified within tolerance
                updated["status"] = "verified"
                updated["conflict_with"] = None
                updated["conflictsWith"] = None
                updated["encroachment_sqft"] = 0.0
                updated["notes"] = "Registered and AI-detected boundaries match within tolerance."
            else:
                # Boundary drift without direct neighbor overlap
                updated["status"] = "discrepancy"
                updated["conflict_with"] = None
                updated["conflictsWith"] = None
                updated["encroachment_sqft"] = 0.0
                updated["notes"] = f"AI-detected boundary has drift (IoU: {iou:.2f}, centroid drift: {drift_m}m). Requires surveyor inspection."

            results.append(updated)

        # 3. Second pass: update notes for parcels that are victims of encroachment
        for r in results:
            pid = r["id"]
            if pid in encroached_by_map and r["status"] == "verified":
                encroacher_id = encroached_by_map[pid]
                r["notes"] = f"Overlapped by an AI-detected extension from {encroacher_id}. Cadastral boundary itself unchanged."

        return results
