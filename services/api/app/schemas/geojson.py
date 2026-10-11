"""Reusable GeoJSON models and spatial geometry serialization helpers."""

import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from shapely import wkb, wkt
from shapely.geometry import mapping
from geoalchemy2.elements import WKBElement, WKTElement


class GeoJSONGeometry(BaseModel):
    """Base model for GeoJSON geometries."""
    type: str
    coordinates: Any


class GeoJSONPoint(GeoJSONGeometry):
    """GeoJSON Point geometry: [longitude, latitude]."""
    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class GeoJSONPolygon(GeoJSONGeometry):
    """GeoJSON Polygon geometry: list of coordinate rings."""
    type: str = "Polygon"
    coordinates: List[List[List[float]]] = Field(..., description="Ring coordinate arrays")


class GeoJSONMultiPolygon(GeoJSONGeometry):
    """GeoJSON MultiPolygon geometry."""
    type: str = "MultiPolygon"
    coordinates: List[List[List[List[float]]]] = Field(..., description="MultiPolygon rings")


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature envelope."""
    type: str = "Feature"
    id: Optional[str] = None
    geometry: Dict[str, Any]
    properties: Dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection envelope."""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature] = Field(default_factory=list)
    properties: Optional[Dict[str, Any]] = None


def _tuples_to_lists(obj: Any) -> Any:
    """Recursively convert coordinate tuples to standard JSON lists."""
    if isinstance(obj, (tuple, list)):
        return [_tuples_to_lists(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: _tuples_to_lists(v) for k, v in obj.items()}
    return obj


def to_geojson_geometry(geom: Any) -> Dict[str, Any]:
    """
    Convert PostGIS / GeoAlchemy2 / Shapely / WKT / WKB / dict to a clean GeoJSON geometry dict.
    """
    if geom is None:
        return {"type": "Point", "coordinates": [0.0, 0.0]}

    if isinstance(geom, dict):
        return _tuples_to_lists(geom)

    # If already a string containing JSON
    if isinstance(geom, str) and geom.strip().startswith("{"):
        try:
            return _tuples_to_lists(json.loads(geom))
        except Exception:
            pass

    # GeoAlchemy2 WKBElement
    if isinstance(geom, WKBElement):
        try:
            shapely_geom = wkb.loads(bytes(geom.data))
            return _tuples_to_lists(mapping(shapely_geom))
        except Exception:
            pass

    # GeoAlchemy2 WKTElement or raw WKT string
    if isinstance(geom, WKTElement) or (isinstance(geom, str) and ("POLYGON" in geom or "POINT" in geom)):
        try:
            wkt_str = str(geom)
            shapely_geom = wkt.loads(wkt_str)
            return _tuples_to_lists(mapping(shapely_geom))
        except Exception:
            pass

    # Fallback to shapely geometry object
    if hasattr(geom, "__geo_interface__"):
        return _tuples_to_lists(geom.__geo_interface__)

    return {"type": "Point", "coordinates": [0.0, 0.0]}
