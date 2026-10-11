import L from 'leaflet';

export type BaseMapType = 'darkMatter' | 'osm' | 'satellite';

export interface MapViewport {
  lat: number;
  lng: number;
  zoom: number;
}

export interface MapState {
  map: L.Map | null;
  baseMap: BaseMapType;
  viewport: MapViewport;
  activeLayers: {
    regionBoundary: boolean;
    riskChoropleth: boolean;
    activeFires: boolean;
    simulationPerimeter: boolean;
    terrain: boolean;
    weather: boolean;
  };
}

export interface MapContextValue {
  map: L.Map | null;
  setMap: (map: L.Map | null) => void;
  baseMap: BaseMapType;
  setBaseMap: (baseMap: BaseMapType) => void;
  activeLayers: MapState['activeLayers'];
  toggleLayer: (layerName: keyof MapState['activeLayers']) => void;
  onMapClick?: (lat: number, lng: number) => void;
  setOnMapClick: (handler?: (lat: number, lng: number) => void) => void;
}
