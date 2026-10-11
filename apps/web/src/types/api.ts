/**
 * API response envelopes and RFC 7807 error types
 */

export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
  request_id?: string | null;
}

export interface ApiErrorResponse {
  error: ApiErrorDetail;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface SystemHealth {
  status: string;
  timestamp: string;
  version: string;
  environment: string;
  services: {
    database: string;
    redis: string;
    celery_broker: string;
  };
}
