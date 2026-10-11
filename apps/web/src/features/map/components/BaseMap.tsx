import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { useMapContext } from '../hooks/useMapContext';
import { APP_CONFIG } from '../../../app/config';

export const BaseMap: React.FC = () => {
  const { map, baseMap } = useMapContext();
  const currentTileLayerRef = useRef<L.TileLayer | null>(null);

  useEffect(() => {
    if (!map) return;

    if (currentTileLayerRef.current) {
      map.removeLayer(currentTileLayerRef.current);
    }

    const config = APP_CONFIG.tileLayers[baseMap] || APP_CONFIG.tileLayers.darkMatter;
    const tileLayer = L.tileLayer(config.url, {
      attribution: config.attribution,
      maxZoom: config.maxZoom,
    });

    tileLayer.addTo(map);
    currentTileLayerRef.current = tileLayer;

    return () => {
      if (currentTileLayerRef.current && map) {
        map.removeLayer(currentTileLayerRef.current);
      }
    };
  }, [map, baseMap]);

  return null;
};
