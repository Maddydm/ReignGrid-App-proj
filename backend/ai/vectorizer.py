import cv2
import numpy as np
from typing import List, Tuple
from shapely.geometry import Polygon
from shapely.validation import make_valid

class PolygonVectorizer:
    """
    Converts raster boundary probability masks into simplified vector polygons
    suitable for GIS and cadastral parcel comparison.
    """
    def __init__(self, min_area: float = 1500.0, simplify_tolerance: float = 2.0):
        self.min_area = min_area
        self.simplify_tolerance = simplify_tolerance

    def vectorize(self, mask: np.ndarray) -> List[Polygon]:
        """
        Extract vector polygons from probability mask.
        """
        # Threshold probability mask to binary
        binary = (mask > 0.30).astype(np.uint8) * 255

        # Morphological closing to seal boundary contours
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Invert to find parcel interior components
        interior = cv2.bitwise_not(closed)

        # Find contours of parcel interiors
        contours, _ = cv2.findContours(interior, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        polygons: List[Polygon] = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue

            # Simplify contour with Douglas-Peucker
            epsilon = 0.015 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) < 3:
                continue

            pts = approx.reshape(-1, 2)
            try:
                poly = Polygon(pts)
                if not poly.is_valid:
                    poly = make_valid(poly)
                if poly.geom_type == 'Polygon' and poly.area >= self.min_area:
                    simplified = poly.simplify(self.simplify_tolerance, preserve_topology=True)
                    polygons.append(simplified)
                elif poly.geom_type == 'MultiPolygon':
                    for part in poly.geoms:
                        if part.area >= self.min_area:
                            polygons.append(part.simplify(self.simplify_tolerance, preserve_topology=True))
            except Exception:
                continue

        return polygons

    @staticmethod
    def polygon_to_points_str(poly: Polygon) -> str:
        """Convert a Shapely Polygon exterior coordinates to REIGNGRID SVG points format 'x1,y1 x2,y2'."""
        coords = list(poly.exterior.coords)[:-1]  # Exclude repeated closing point
        return " ".join(f"{int(round(x))},{int(round(y))}" for x, y in coords)

    @staticmethod
    def points_str_to_polygon(points_str: str) -> Polygon:
        """Parse 'x1,y1 x2,y2' string into Shapely Polygon."""
        coords = []
        for pair in points_str.strip().split():
            x, y = pair.split(",")
            coords.append((float(x), float(y)))
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = make_valid(poly)
        return poly
