// REIGNGRID Frontend Configuration
const REIGNGRID_CONFIG = {
  PRODUCT_NAME: "REIGNGRID",
  TAGLINE: "Geospatial Intelligence for the Physical World.",
  
  // Backend REST API Base
  API_BASE: window.location.origin,

  // Supabase Configuration (Optional direct connection)
  SUPABASE_URL: window.ENV_SUPABASE_URL || "",
  SUPABASE_ANON_KEY: window.ENV_SUPABASE_ANON_KEY || "",

  // Free Esri World Imagery Satellite Tile Source (High-resolution global satellite)
  SATELLITE_TILE_URL: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",

  // Geographic anchor: SRM Institute of Science & Technology, Ramapuram, Chennai
  DEFAULT_CENTER: [80.1816, 13.0328],
  DEFAULT_ZOOM: 17.2,
};

// Backwards compatibility alias
const LANDSIGHT_CONFIG = REIGNGRID_CONFIG;
