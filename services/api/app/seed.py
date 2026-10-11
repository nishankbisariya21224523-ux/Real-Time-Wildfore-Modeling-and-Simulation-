"""Development-only database seeding script for local testing and CI/CD."""

import sys
import uuid
from datetime import datetime, timezone, timedelta
from geoalchemy2.elements import WKTElement

from .core.database import SessionLocal, engine
from .core.logging import logger
from .models.region import Region
from .models.grid_cell import GridCell
from .models.environmental_observation import EnvironmentalObservation
from .models.fire_event import FireEvent


def seed_database():
    """Seed sample development data into PostGIS database."""
    if SessionLocal is None:
        logger.error("Database is not configured. Cannot run seed script.")
        return False

    db = SessionLocal()
    try:
        logger.info("Starting database seeding process...")

        # 1. Garhwal Forest Division, Uttarakhand
        garhwal_id = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
        existing_garhwal = db.query(Region).filter(Region.id == garhwal_id).first()
        if not existing_garhwal:
            garhwal = Region(
                id=garhwal_id,
                code="UTTARAKHAND_GARHWAL",
                name="Garhwal Forest Division (DEMO SEED)",
                state="Uttarakhand",
                area_sqkm=2840.50,
                boundary=WKTElement("POLYGON((78.50 30.10, 79.10 30.10, 79.10 30.40, 78.50 30.40, 78.50 30.10))", srid=4326),
            )
            db.add(garhwal)
            logger.info("Seeded Region: Garhwal Forest Division")

        # 2. Wayanad Wildlife Sanctuary, Kerala
        wayanad_id = uuid.UUID("7ca85f64-5717-4562-b3fc-2c963f66afa7")
        existing_wayanad = db.query(Region).filter(Region.id == wayanad_id).first()
        if not existing_wayanad:
            wayanad = Region(
                id=wayanad_id,
                code="WESTERN_GHATS_WAYANAD",
                name="Wayanad Wildlife Sanctuary (DEMO SEED)",
                state="Kerala",
                area_sqkm=344.40,
                boundary=WKTElement("POLYGON((76.15 11.60, 76.35 11.60, 76.35 11.80, 76.15 11.80, 76.15 11.60))", srid=4326),
            )
            db.add(wayanad)
            logger.info("Seeded Region: Wayanad Wildlife Sanctuary")

        # 3. Sample 500m Grid Cell in Garhwal
        cell_id = uuid.UUID("9bc12345-0000-0000-0000-000000000129")
        existing_cell = db.query(GridCell).filter(GridCell.id == cell_id).first()
        if not existing_cell:
            cell = GridCell(
                id=cell_id,
                region_id=garhwal_id,
                cell_code="GARHWAL_500M_00129",
                centroid=WKTElement("POINT(78.7525 30.2025)", srid=4326),
                geometry=WKTElement("POLYGON((78.750 30.200, 78.755 30.200, 78.755 30.205, 78.750 30.205, 78.750 30.200))", srid=4326),
                resolution_meters=500,
                elevation_m=1420.0,
                slope_deg=22.4,
                aspect_deg=135.0,
                fuel_type="Chir_Pine",
            )
            db.add(cell)
            logger.info("Seeded 500m GridCell: GARHWAL_500M_00129")

        # 4. Sample Environmental Observation
        obs_time = datetime.now(timezone.utc) - timedelta(hours=2)
        existing_obs = db.query(EnvironmentalObservation).filter(
            EnvironmentalObservation.grid_cell_id == cell_id,
            EnvironmentalObservation.observation_time == obs_time
        ).first()
        if not existing_obs:
            obs = EnvironmentalObservation(
                id=uuid.uuid4(),
                grid_cell_id=cell_id,
                observation_time=obs_time,
                temperature_c=34.2,
                relative_humidity_pct=21.0,
                wind_speed_ms=7.4,
                wind_direction_deg=235.0,
                precipitation_mm=0.0,
                ndvi=0.34,
                ndwi=-0.15,
                fwi=28.5,
            )
            db.add(obs)
            logger.info("Seeded Environmental Observation for cell")

        # 5. Sample Active Fire Event
        fire_id = uuid.UUID("f8a9e712-4523-41a3-b3c1-019283746554")
        existing_fire = db.query(FireEvent).filter(FireEvent.id == fire_id).first()
        if not existing_fire:
            fire = FireEvent(
                id=fire_id,
                grid_cell_id=cell_id,
                source="VIIRS_NOAA20",
                detected_at=datetime.now(timezone.utc) - timedelta(hours=1),
                brightness_temp_k=348.6,
                frp_mw=42.1,
                confidence_pct=88.0,
                location=WKTElement("POINT(78.7523 30.2104)", srid=4326),
                is_active=True,
            )
            db.add(fire)
            logger.info("Seeded Active Fire Event: VIIRS_NOAA20")

        db.commit()
        logger.info("Database seeding successfully completed!")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed database: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
