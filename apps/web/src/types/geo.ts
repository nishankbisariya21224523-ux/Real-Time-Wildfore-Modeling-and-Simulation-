/**
 * RFC 7946 Compliant GeoJSON Types
 */

export type Position = [number, number] | [number, number, number]; // [longitude, latitude, elevation?]

export type BoundingBox = [number, number, number, number]; // [minLon, minLat, maxLon, maxLat]

export interface PointGeometry {
  type: 'Point';
  coordinates: Position;
}

export interface MultiPointGeometry {
  type: 'MultiPoint';
  coordinates: Position[];
}

export interface LineStringGeometry {
  type: 'LineString';
  coordinates: Position[];
}

export interface MultiLineStringGeometry {
  type: 'MultiLineString';
  coordinates: Position[][];
}

export interface PolygonGeometry {
  type: 'Polygon';
  coordinates: Position[][];
}

export interface MultiPolygonGeometry {
  type: 'MultiPolygon';
  coordinates: Position[][][];
}

export type GeoJSONGeometry =
  | PointGeometry
  | MultiPointGeometry
  | LineStringGeometry
  | MultiLineStringGeometry
  | PolygonGeometry
  | MultiPolygonGeometry;

export interface GeoJSONFeature<G extends GeoJSONGeometry = GeoJSONGeometry, P = Record<string, unknown>> {
  type: 'Feature';
  id?: string | number;
  geometry: G;
  properties: P;
  bbox?: BoundingBox;
}

export interface GeoJSONFeatureCollection<
  G extends GeoJSONGeometry = GeoJSONGeometry,
  P = Record<string, unknown>
> {
  type: 'FeatureCollection';
  features: GeoJSONFeature<G, P>[];
  bbox?: BoundingBox;
}
