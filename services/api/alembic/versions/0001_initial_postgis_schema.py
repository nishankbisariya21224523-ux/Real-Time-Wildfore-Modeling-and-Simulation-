"""Initial PostGIS schema migration for all 7 tables.

Revision ID: 0001_initial_postgis_schema
Revises: None
Create Date: 2026-10-05 23:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision: str = '0001_initial_postgis_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extensions (PostgreSQL only)
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')

    # 2. regions table
    op.create_table(
        'regions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('boundary', geoalchemy2.Geometry(geometry_type='POLYGON', srid=4326), nullable=False),
        sa.Column('area_sqkm', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_regions_code', 'regions', ['code'])
    op.create_index('idx_regions_state', 'regions', ['state'])

    # 3. grid_cells table
    op.create_table(
        'grid_cells',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cell_code', sa.String(length=100), nullable=False, unique=True),
        sa.Column('centroid', geoalchemy2.Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('geometry', geoalchemy2.Geometry(geometry_type='POLYGON', srid=4326), nullable=False),
        sa.Column('resolution_meters', sa.Integer(), nullable=False, server_default='500'),
        sa.Column('elevation_m', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('slope_deg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('aspect_deg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('fuel_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_grid_cells_region', 'grid_cells', ['region_id'])

    # 4. fire_events table
    op.create_table(
        'fire_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('grid_cell_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('grid_cells.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('brightness_temp_k', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('frp_mw', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('confidence_pct', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('location', geoalchemy2.Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_fire_events_detected_at', 'fire_events', ['detected_at'])
    op.create_index('idx_fire_events_is_active', 'fire_events', ['is_active'])

    # 5. environmental_observations table
    op.create_table(
        'environmental_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('grid_cell_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('grid_cells.id', ondelete='CASCADE'), nullable=False),
        sa.Column('observation_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('temperature_c', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('relative_humidity_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('wind_speed_ms', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('wind_direction_deg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('precipitation_mm', sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column('ndvi', sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column('ndwi', sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column('fwi', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('grid_cell_id', 'observation_time', name='uq_cell_obs_time'),
    )
    op.create_index('idx_env_obs_cell_time', 'environmental_observations', ['grid_cell_id', 'observation_time'])

    # 6. risk_predictions table
    op.create_table(
        'risk_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('grid_cell_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('grid_cells.id', ondelete='CASCADE'), nullable=False),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('valid_for_date', sa.Date(), nullable=False),
        sa.Column('risk_probability', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('risk_class', sa.String(length=20), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('risk_probability >= 0.0 AND risk_probability <= 1.0', name='chk_risk_prob_range'),
        sa.CheckConstraint("risk_class IN ('LOW', 'MODERATE', 'HIGH', 'EXTREME')", name='chk_risk_class_valid'),
        sa.UniqueConstraint('grid_cell_id', 'valid_for_date', 'model_version', name='uq_cell_risk_pred'),
    )
    op.create_index('idx_risk_pred_region_date', 'risk_predictions', ['region_id', 'valid_for_date'])

    # 7. simulations table
    op.create_table(
        'simulations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ignition_location', geoalchemy2.Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('ignition_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_hours', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='QUEUED'),
        sa.Column('total_area_burned_ha', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.0'),
        sa.Column('model_version', sa.String(length=50), nullable=False, server_default='ca-baseline-v1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('QUEUED', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')", name='chk_simulation_status'),
    )
    op.create_index('idx_simulations_status', 'simulations', ['status'])
    op.create_index('idx_simulations_region', 'simulations', ['region_id'])

    # 8. simulation_steps table
    op.create_table(
        'simulation_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('simulation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('simulations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('step_hour', sa.Integer(), nullable=False),
        sa.Column('burned_area_ha', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('spread_velocity_kmh', sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column('spread_direction_deg', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('intensity_mw', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('perimeter_geom', geoalchemy2.Geometry(geometry_type='POLYGON', srid=4326), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('step_hour >= 0 AND step_hour <= 12', name='chk_sim_step_hour_range'),
        sa.UniqueConstraint('simulation_id', 'step_hour', name='uq_sim_step_hour'),
    )
    op.create_index('idx_sim_steps_sim_hour', 'simulation_steps', ['simulation_id', 'step_hour'])


def downgrade() -> None:
    op.drop_table('simulation_steps')
    op.drop_table('simulations')
    op.drop_table('risk_predictions')
    op.drop_table('environmental_observations')
    op.drop_table('fire_events')
    op.drop_table('grid_cells')
    op.drop_table('regions')
