-- Seed Data for Forest Fire Platform: Reference Regions & Sample 500m Grid Cells

-- 1. Garhwal Forest Division, Uttarakhand
INSERT INTO regions (id, code, name, state, area_sqkm, boundary)
VALUES (
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'UTTARAKHAND_GARHWAL',
    'Garhwal Forest Division',
    'Uttarakhand',
    2840.50,
    ST_GeomFromText('POLYGON((78.50 30.10, 79.10 30.10, 79.10 30.40, 78.50 30.40, 78.50 30.10))', 4326)
) ON CONFLICT (code) DO NOTHING;

-- 2. Wayanad Wildlife Sanctuary, Kerala (Western Ghats)
INSERT INTO regions (id, code, name, state, area_sqkm, boundary)
VALUES (
    '7ca85f64-5717-4562-b3fc-2c963f66afa7',
    'WESTERN_GHATS_WAYANAD',
    'Wayanad Wildlife Sanctuary',
    'Kerala',
    344.40,
    ST_GeomFromText('POLYGON((76.15 11.60, 76.35 11.60, 76.35 11.80, 76.15 11.80, 76.15 11.60))', 4326)
) ON CONFLICT (code) DO NOTHING;

-- Sample Seed 500m Grid Cell in Garhwal
INSERT INTO grid_cells (id, region_id, cell_code, centroid, geometry, resolution_meters, elevation_m, slope_deg, aspect_deg, fuel_type)
VALUES (
    '9bc12345-0000-0000-0000-000000000129',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'GARHWAL_500M_00129',
    ST_SetSRID(ST_Point(78.7525, 30.2025), 4326),
    ST_GeomFromText('POLYGON((78.750 30.200, 78.755 30.200, 78.755 30.205, 78.750 30.205, 78.750 30.200))', 4326),
    500,
    1420.0,
    22.4,
    135.0,
    'Chir_Pine'
) ON CONFLICT (cell_code) DO NOTHING;
