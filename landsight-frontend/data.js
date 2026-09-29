// REIGNGRID Cadastral Dataset — WGS84 GeoJSON anchored over SRM Ramapuram, Chennai
// Sector 12-B baseline data with numeric area_sqft and PostGIS coordinates.

const WGS84_PARCELS = [
  {
    id: "PCL-1042",
    owner: "Lakshmi Narayanan",
    area_sqft: 22215.6,
    status: "verified",
    lastSynced: "2024-11-02",
    notes: "Registered and AI-detected boundaries match within 2.1% tolerance.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.1805, 13.0332], [80.18092, 13.0332], [80.18092, 13.03282], [80.1805, 13.03282], [80.1805, 13.0332]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.1805, 13.0332], [80.18092, 13.0332], [80.18092, 13.03282], [80.1805, 13.03282], [80.1805, 13.0332]]]
    },
    iou_score: 0.98,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.0,
    priority: "LOW"
  },
  {
    id: "PCL-1043",
    owner: "S. Kumaravel",
    area_sqft: 19166.4,
    status: "verified",
    lastSynced: "2024-11-02",
    notes: "Registered and AI-detected boundaries match within 3.0% tolerance.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18094, 13.0332], [80.18136, 13.0332], [80.18136, 13.03282], [80.18094, 13.03282], [80.18094, 13.0332]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.18094, 13.0332], [80.18136, 13.0332], [80.18136, 13.03282], [80.18094, 13.03282], [80.18094, 13.0332]]]
    },
    iou_score: 0.97,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.1,
    priority: "LOW"
  },
  {
    id: "PCL-1044",
    owner: "Devika Raman",
    area_sqft: 26571.6,
    status: "discrepancy",
    lastSynced: "2024-11-02",
    notes: "AI-detected boundary extends ~340 sq. ft east into PCL-1045. Flagged for field verification.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18138, 13.0332], [80.1818, 13.0332], [80.1818, 13.03282], [80.18138, 13.03282], [80.18138, 13.0332]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.18146, 13.0332], [80.18188, 13.0332], [80.18188, 13.03282], [80.18146, 13.03282], [80.18146, 13.0332]]]
    },
    iou_score: 0.81,
    conflict_with: "PCL-1045",
    encroachment_sqft: 340.0,
    displacement_m: 2.4,
    priority: "HIGH"
  },
  {
    id: "PCL-1045",
    owner: "Arjun Mehta",
    area_sqft: 20908.8,
    status: "verified",
    lastSynced: "2024-11-02",
    notes: "Overlapped by an AI-detected extension from PCL-1044. Cadastral boundary itself unchanged.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18182, 13.0332], [80.18224, 13.0332], [80.18224, 13.03282], [80.18182, 13.03282], [80.18182, 13.0332]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.18182, 13.0332], [80.18224, 13.0332], [80.18224, 13.03282], [80.18182, 13.03282], [80.18182, 13.0332]]]
    },
    iou_score: 0.96,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.1,
    priority: "LOW"
  },
  {
    id: "PCL-1046",
    owner: "Priya Sundaram",
    area_sqft: 16988.4,
    status: "pending",
    lastSynced: "2024-10-18",
    notes: "High-resolution imagery captured; awaiting AI segmentation pass.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18226, 13.0332], [80.18268, 13.0332], [80.18268, 13.03282], [80.18226, 13.03282], [80.18226, 13.0332]]]
    },
    detected_geom: null,
    iou_score: null,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.0,
    priority: "MEDIUM"
  },
  {
    id: "PCL-1047",
    owner: "T. Ravichandran",
    area_sqft: 23958.0,
    status: "verified",
    lastSynced: "2024-11-02",
    notes: "Registered and AI-detected boundaries match within 1.2% tolerance.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.1805, 13.0328], [80.18092, 13.0328], [80.18092, 13.03242], [80.1805, 13.03242], [80.1805, 13.0328]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.1805, 13.0328], [80.18092, 13.0328], [80.18092, 13.03242], [80.1805, 13.03242], [80.1805, 13.0328]]]
    },
    iou_score: 0.99,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.0,
    priority: "LOW"
  },
  {
    id: "PCL-1048",
    owner: "Meena Krishnan",
    area_sqft: 25264.8,
    status: "discrepancy",
    lastSynced: "2024-11-02",
    notes: "AI-detected boundary overlaps PCL-1049 by ~210 sq. ft — possible fence encroachment.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18094, 13.0328], [80.18136, 13.0328], [80.18136, 13.03242], [80.18094, 13.03242], [80.18094, 13.0328]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.181, 13.0328], [80.18142, 13.0328], [80.18142, 13.03242], [80.181, 13.03242], [80.181, 13.0328]]]
    },
    iou_score: 0.83,
    conflict_with: "PCL-1049",
    encroachment_sqft: 210.0,
    displacement_m: 1.8,
    priority: "HIGH"
  },
  {
    id: "PCL-1049",
    owner: "Suresh Babu",
    area_sqft: 20473.2,
    status: "verified",
    lastSynced: "2024-11-02",
    notes: "Overlapped by an AI-detected extension from PCL-1048. Cadastral boundary itself unchanged.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18138, 13.0328], [80.1818, 13.0328], [80.1818, 13.03242], [80.18138, 13.03242], [80.18138, 13.0328]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.18138, 13.0328], [80.1818, 13.0328], [80.1818, 13.03242], [80.18138, 13.03242], [80.18138, 13.0328]]]
    },
    iou_score: 0.95,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.2,
    priority: "LOW"
  },
  {
    id: "PCL-1050",
    owner: "Anitha Raghavan",
    area_sqft: 21780.0,
    status: "verified",
    lastSynced: "2024-11-02",
    notes: "Registered and AI-detected boundaries match within 2.8% tolerance.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18182, 13.0328], [80.18224, 13.0328], [80.18224, 13.03242], [80.18182, 13.03242], [80.18182, 13.0328]]]
    },
    detected_geom: {
      type: "Polygon",
      coordinates: [[[80.18182, 13.0328], [80.18224, 13.0328], [80.18224, 13.03242], [80.18182, 13.03242], [80.18182, 13.0328]]]
    },
    iou_score: 0.97,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.1,
    priority: "LOW"
  },
  {
    id: "PCL-1051",
    owner: "K. Balamurugan",
    area_sqft: 17859.6,
    status: "pending",
    lastSynced: "2024-10-18",
    notes: "High-resolution imagery captured; awaiting AI segmentation pass.",
    registered_geom: {
      type: "Polygon",
      coordinates: [[[80.18226, 13.0328], [80.18268, 13.0328], [80.18268, 13.03242], [80.18226, 13.03242], [80.18226, 13.0328]]]
    },
    detected_geom: null,
    iou_score: null,
    conflict_with: null,
    encroachment_sqft: 0.0,
    displacement_m: 0.0,
    priority: "MEDIUM"
  }
];

// Fallback KPIs matching Screen 2 Command Center
const DEFAULT_KPI = {
  total_parcels: 1248,
  verified_parcels: 1116,
  needs_review: 84,
  discrepancies: 48,
  monitored_acres: 642.8,
  sector: "Sector 12-B",
  location: "SRM Ramapuram, Chennai",
  gsd_m: 0.05,
  last_sync: "02 Nov 2024",
  ai_engine_status: "ONLINE"
};

// Formatting helpers
function formatAreaAcres(areaSqft) {
  if (!areaSqft || isNaN(areaSqft)) return "0.00 acres (0 sq ft)";
  const acres = (areaSqft / 43560.0).toFixed(2);
  const sqft = Math.round(areaSqft).toLocaleString();
  return `${acres} acres (${sqft} sq ft)`;
}

function formatAreaShort(areaSqft) {
  if (!areaSqft || isNaN(areaSqft)) return "0 sq ft";
  const acres = (areaSqft / 43560.0).toFixed(2);
  return `${acres} ac`;
}
