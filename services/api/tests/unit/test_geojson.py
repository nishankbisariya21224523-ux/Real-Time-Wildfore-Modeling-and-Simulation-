"""Unit tests for GeoJSON serialization and geometry conversions."""

from shapely.geometry import Point, Polygon
from services.api.app.schemas.geojson import (
    to_geojson_geometry,
    GeoJSONPoint,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
)


def test_shapely_to_geojson():
    """Verify Shapely geometries convert to valid GeoJSON geometry dictionaries."""
    pt = Point(78.7523, 30.2104)
    geom_dict = to_geojson_geometry(pt)
    assert geom_dict["type"] == "Point"
    assert geom_dict["coordinates"] == [78.7523, 30.2104]

    poly = Polygon([[78.5, 30.1], [79.1, 30.1], [79.1, 30.4], [78.5, 30.4], [78.5, 30.1]])
    poly_dict = to_geojson_geometry(poly)
    assert poly_dict["type"] == "Polygon"
    assert len(poly_dict["coordinates"][0]) == 5


def test_wkt_string_to_geojson():
    """Verify WKT string converts to GeoJSON geometry."""
    wkt_str = "POINT(78.5 30.2)"
    res = to_geojson_geometry(wkt_str)
    assert res["type"] == "Point"
    assert res["coordinates"] == [78.5, 30.2]


def test_feature_collection_construction():
    """Verify GeoJSON FeatureCollection serialization."""
    f = GeoJSONFeature(
        id="test-1",
        geometry={"type": "Point", "coordinates": [78.0, 30.0]},
        properties={"metric": 42},
    )
    fc = GeoJSONFeatureCollection(features=[f], properties={"count": 1})
    d = fc.model_dump()
    assert d["type"] == "FeatureCollection"
    assert len(d["features"]) == 1
    assert d["features"][0]["properties"]["metric"] == 42
