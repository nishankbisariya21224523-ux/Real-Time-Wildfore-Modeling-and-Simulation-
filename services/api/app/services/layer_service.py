"""Service layer managing static and environmental GIS layers."""

from typing import Dict, Any, List
from ..schemas.layers import LayerMetadataResponse, LayerCatalogItem
from ..core.exceptions import ValidationException

ALLOWED_LAYERS = {
    "elevation": {
        "unit": "meters above sea level",
        "resolution_meters": 500,
        "source": "CartoDEM / SRTM 30m Resampled",
        "legend": {
            "low": "< 1000m",
            "medium": "1000m - 2000m",
            "high": "> 2000m",
        },
    },
    "slope": {
        "unit": "degrees",
        "resolution_meters": 500,
        "source": "Derived Topographical Gradient",
        "legend": {
            "gentle": "0 - 10 deg",
            "moderate": "10 - 25 deg",
            "steep": "25 - 45 deg",
            "extreme": "> 45 deg",
        },
    },
    "fuel": {
        "unit": "standardized fuel classification",
        "resolution_meters": 500,
        "source": "ISRO Bhuvan Land Cover 2024",
        "legend": {
            "1": "Dense Pine Forest (High Flammability)",
            "2": "Deciduous Broadleaf (Moderate)",
            "3": "Dry Shrubland (High)",
            "4": "Grassland / Agricultural (Low-Moderate)",
        },
    },
    "weather": {
        "unit": "atmospheric precursors",
        "resolution_meters": 500,
        "source": "IMD API / ERA5 Reanalysis",
        "legend": {
            "temperature": "Celsius",
            "relative_humidity": "Percentage",
            "wind_speed": "m/s",
            "fwi": "Fire Weather Index",
        },
    },
    "fire-history": {
        "unit": "burn scar frequency",
        "resolution_meters": 500,
        "source": "2015-2025 Historical Burn Scars",
        "legend": {
            "burned": "Recorded Fire Ignition / Scar",
            "unburned": "No Historical Event",
        },
    },
}


class LayerService:
    """Service managing layer metadata and access."""

    def get_layer_metadata(self, layer_type: str, region_id: str) -> LayerMetadataResponse:
        lt = layer_type.lower()
        if lt not in ALLOWED_LAYERS:
            raise ValidationException(
                message=f"Unsupported layer_type '{layer_type}'. Supported: {', '.join(sorted(ALLOWED_LAYERS.keys()))}",
                details={"allowed_layers": list(ALLOWED_LAYERS.keys())},
            )

        info = ALLOWED_LAYERS[lt]
        return LayerMetadataResponse(
            layer_type=lt,
            region_id=region_id,
            resolution_meters=info["resolution_meters"],
            legend=info["legend"],
            source=info["source"],
        )

    def list_layers(self) -> List[LayerCatalogItem]:
        """Return catalog of available GIS layers."""
        categories = {
            "elevation": ("Elevation DEM", "terrain", "CartoDEM 30m Resampled to 500m"),
            "slope": ("Topographic Slope", "terrain", "Slope gradient derived from CartoDEM"),
            "fuel": ("Fuel Classification", "vegetation", "ISRO Bhuvan Land Cover fuel models"),
            "weather": ("Weather Conditions", "weather", "IMD & ERA5 meteorological precursors"),
            "fire-history": ("Historical Fire Perimeters", "fire", "Historical burn scar frequencies"),
        }
        items = []
        for k, info in ALLOWED_LAYERS.items():
            name, cat, desc = categories.get(k, (k.title(), "terrain", info["source"]))
            items.append(
                LayerCatalogItem(
                    id=k,
                    name=name,
                    category=cat,
                    description=desc,
                    source=info["source"],
                    is_available=True,
                    resolution=f"{info['resolution_meters']}m",
                )
            )
        return items
