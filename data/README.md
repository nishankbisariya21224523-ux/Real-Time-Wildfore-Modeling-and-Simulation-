# Data Storage Organization

This directory manages datasets across raw, processed, and sample stages. In production and containerized environments, heavy binary rasters and satellite archives are stored in external object storage (e.g., S3/GCS/MinIO) with spatial indexing and metadata maintained in PostgreSQL/PostGIS.

## Directory Structure

- `raw/`: Unprocessed satellite files, DEM rasters, raw weather feeds, and active fire shapefiles/GeoJSONs.
- `processed/`: Aligned, clipped, and normalized raster and vector datasets standardized onto the 500m × 500m common spatial grid.
- `sample/`: Lightweight synthetic or truncated geographic samples for local testing and CI/CD without requiring multi-gigabyte downloads.

## Spatial Reference & Resolution
- Common Coordinate Reference System (CRS): EPSG:4326 (WGS 84) for geographic coordinates, EPSG:3857 for web mapping, and UTM projections (e.g., EPSG:32643 / EPSG:32644) for accurate metric 500m grid cell calculations across Indian subregions.
- Target Spatial Resolution: 500m × 500m grid cells.
- Temporal Cadence: Daily composites for fire-risk precursor features, hourly slices for active spread simulation.
