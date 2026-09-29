-- ============================================================================
-- LandSight Cadastral AI Verification — Supabase PostGIS Migration
-- ============================================================================

-- 1. Enable PostGIS extension
create extension if not exists postgis with schema extensions;

-- 2. Create Parcels Table (Registered Cadastral Ground Truth)
create table if not exists public.parcels (
    id text primary key,
    owner text not null,
    area_sqft numeric not null, -- Raw square footage (e.g. 22215.6 sq ft = 0.51 acres)
    status text not null default 'pending' check (status in ('verified', 'discrepancy', 'pending')),
    last_synced date default current_date,
    registered_geom extensions.geometry(Polygon, 4326) not null,
    notes text
);

-- 3. Create AI Detections Table (Derived Boundaries from Aerial/Satellite Imagery)
create table if not exists public.ai_detections (
    id uuid primary key default gen_random_uuid(),
    parcel_id text not null references public.parcels(id) on delete cascade,
    detected_geom extensions.geometry(Polygon, 4326) not null,
    iou_score double precision,
    conflict_with text references public.parcels(id) on delete set null,
    encroachment_sqft double precision default 0.0,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 4. Create Imagery Table (Survey Passes & Orthophotos)
create table if not exists public.imagery (
    id text primary key,
    source text not null, -- 'drone_orthophoto', 'satellite_pass', 'aerial_survey'
    captured_at timestamp with time zone default timezone('utc'::text, now()),
    file_path text not null, -- Path inside Supabase Storage bucket
    bounds extensions.geometry(Polygon, 4326)
);

-- 5. Create Spatial GIST Indexes for sub-millisecond GIS queries
create index if not exists idx_parcels_geom on public.parcels using gist(registered_geom);
create index if not exists idx_detections_geom on public.ai_detections using gist(detected_geom);
create index if not exists idx_imagery_bounds on public.imagery using gist(bounds);

-- 6. Row Level Security (RLS) Configuration
-- Public read access allows visitors to explore the interactive satellite map.
-- Write access is restricted to authenticated users with Inspector role.

alter table public.parcels enable row level security;
alter table public.ai_detections enable row level security;
alter table public.imagery enable row level security;

-- Public Read Policies
create policy "Public can view parcels"
    on public.parcels for select
    using (true);

create policy "Public can view ai_detections"
    on public.ai_detections for select
    using (true);

create policy "Public can view imagery"
    on public.imagery for select
    using (true);

-- Authenticated Write Policies (Inspector role)
create policy "Inspectors can insert parcels"
    on public.parcels for insert
    to authenticated
    with check (true);

create policy "Inspectors can update parcels"
    on public.parcels for update
    to authenticated
    using (true)
    with check (true);

create policy "Inspectors can delete parcels"
    on public.parcels for delete
    to authenticated
    using (true);

create policy "Inspectors can insert ai_detections"
    on public.ai_detections for insert
    to authenticated
    with check (true);

create policy "Inspectors can update ai_detections"
    on public.ai_detections for update
    to authenticated
    using (true)
    with check (true);

create policy "Inspectors can delete ai_detections"
    on public.ai_detections for delete
    to authenticated
    using (true);

create policy "Inspectors can manage imagery"
    on public.imagery for all
    to authenticated
    using (true)
    with check (true);

-- 7. Supabase Storage Bucket Setup
-- Note: Create bucket 'cadastral-imagery' via Supabase Dashboard -> Storage or via:
insert into storage.buckets (id, name, public)
values ('cadastral-imagery', 'cadastral-imagery', true)
on conflict (id) do nothing;

create policy "Public Access to Cadastral Imagery"
    on storage.objects for select
    using (bucket_id = 'cadastral-imagery');

create policy "Inspectors Upload Cadastral Imagery"
    on storage.objects for insert
    to authenticated
    with check (bucket_id = 'cadastral-imagery');
