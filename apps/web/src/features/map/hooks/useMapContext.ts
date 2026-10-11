import { createContext, useContext } from 'react';
import { MapContextValue } from '../types/map';

export const MapContext = createContext<MapContextValue | null>(null);

export function useMapContext(): MapContextValue {
  const context = useContext(MapContext);
  if (!context) {
    throw new Error('useMapContext must be used within a MapContainer with MapContext.Provider');
  }
  return context;
}
