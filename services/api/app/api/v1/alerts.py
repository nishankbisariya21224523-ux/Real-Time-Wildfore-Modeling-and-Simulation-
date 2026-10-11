"""FastAPI Router for Telegram Emergency Wildfire Civil Alerts."""
from fastapi import APIRouter, Depends, status
from ...schemas.alerts import (
    TelegramAlertRequest,
    TelegramAlertResponse,
    TelegramStatusResponse,
)
from ...services.telegram_service import TelegramService
from ...dependencies.services import get_telegram_service

router = APIRouter(prefix="/alerts", tags=["Emergency Alerts"])


@router.get(
    "/status",
    response_model=TelegramStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check Telegram Emergency Broadcast Gateway Status",
)
async def get_telegram_status(
    service: TelegramService = Depends(get_telegram_service),
) -> TelegramStatusResponse:
    """Returns the operational status of the Telegram civil alert gateway."""
    return TelegramStatusResponse(
        provider="Telegram Emergency Alerts",
        is_configured=service.is_configured,
        default_chat_id=service.default_chat_id,
        status="live_bot_active" if service.is_configured else "simulation_mode_ready",
    )


@router.post(
    "/telegram",
    response_model=TelegramAlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Broadcast Wildfire Emergency Civil Alert to Residents via Telegram",
)
async def broadcast_telegram_alert(
    payload: TelegramAlertRequest,
    service: TelegramService = Depends(get_telegram_service),
) -> TelegramAlertResponse:
    """
    Broadcasts an urgent wildfire alert message to the regional Telegram channel/group
    with threat levels, evacuation directives, and safety instructions.
    """
    result = await service.broadcast_alert(
        region_name=payload.region_name,
        threat_level=payload.threat_level,
        fire_danger_index=payload.fire_danger_index,
        evacuation_status=payload.evacuation_status,
        safety_instructions=payload.safety_instructions,
        custom_note=payload.custom_note,
        target_chat_id=payload.target_chat_id,
    )
    return TelegramAlertResponse(**result)
