"""Pydantic schemas for Telegram emergency civil alerts."""
from typing import List, Optional
from pydantic import BaseModel, Field


class TelegramAlertRequest(BaseModel):
    region_name: str = Field(..., description="Target wildfire affected region name")
    threat_level: str = Field("HIGH", description="Current threat severity category")
    fire_danger_index: float = Field(..., ge=0.0, le=100.0, description="Composite FDI (0-100)")
    evacuation_status: str = Field("ADVISORY", description="Current civil alert/evacuation status")
    safety_instructions: Optional[List[str]] = Field(
        None, description="Custom tactical instructions for local residents"
    )
    custom_note: Optional[str] = Field(
        None, description="Additional notes or road closure notices"
    )
    target_chat_id: Optional[str] = Field(
        None, description="Optional override for target Telegram chat/channel ID"
    )


class TelegramAlertResponse(BaseModel):
    status: str
    provider: str
    channel: str
    message_id: Optional[int] = None
    formatted_message: str
    timestamp: str


class TelegramStatusResponse(BaseModel):
    provider: str = "Telegram Emergency Alerts"
    is_configured: bool
    default_chat_id: Optional[str] = None
    status: str
