/**
 * Telegram Emergency Wildfire Alerts API Client
 */
import { httpClient } from './client';

export interface TelegramAlertPayload {
  region_name: string;
  threat_level: string;
  fire_danger_index: number;
  evacuation_status: string;
  safety_instructions?: string[];
  custom_note?: string;
  target_chat_id?: string;
}

export interface TelegramAlertResult {
  status: string;
  provider: string;
  channel: string;
  message_id?: number;
  formatted_message: string;
  timestamp: string;
}

export interface TelegramStatusResult {
  provider: string;
  is_configured: boolean;
  default_chat_id?: string;
  status: string;
}

export async function fetchTelegramStatus(): Promise<TelegramStatusResult> {
  return httpClient.request<TelegramStatusResult>('/alerts/status');
}

export async function broadcastTelegramAlert(
  payload: TelegramAlertPayload
): Promise<TelegramAlertResult> {
  return httpClient.request<TelegramAlertResult>('/alerts/telegram', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
