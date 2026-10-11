from typing import List
from fastapi import APIRouter, Path, Query, Depends, status
from ...schemas.layers import LayerMetadataResponse, LayerCatalogItem
from ...services.layer_service import LayerService
from ...dependencies.services import get_layer_service

router = APIRouter(prefix="/layers", tags=["Layers"])


@router.get(
    "",
    response_model=List[LayerCatalogItem],
    status_code=status.HTTP_200_OK,
    summary="List Environmental GIS Layers Catalog"
)
async def list_layers(
    service: LayerService = Depends(get_layer_service),
) -> List[LayerCatalogItem]:
    """Retrieve the full catalog of operational and reference GIS layers."""
    return service.list_layers()


@router.get(
    "/{layer_type}",
    response_model=LayerMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Environmental GIS Layer Information & Legend"
)
async def get_layer_metadata(
    layer_type: str = Path(..., description="Layer category: elevation | slope | fuel | weather | fire-history"),
    region_id: str = Query(..., description="Target region UUID"),
    service: LayerService = Depends(get_layer_service),
) -> LayerMetadataResponse:
    """Retrieve metadata, resolution, and classification legend for static GIS layers."""
    return service.get_layer_metadata(layer_type=layer_type, region_id=region_id)
