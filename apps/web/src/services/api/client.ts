/**
 * Core HTTP Client with RFC 7807 problem details parsing and timeout management
 */

import { APP_CONFIG } from '../../app/config';
import { ApiErrorDetail, ApiErrorResponse } from '../../types/api';

export class ApiError extends Error {
  public readonly code: string;
  public readonly details?: Record<string, unknown> | null;
  public readonly requestId?: string | null;
  public readonly status: number;

  constructor(status: number, errorDetail: ApiErrorDetail) {
    super(errorDetail.message);
    this.name = 'ApiError';
    this.status = status;
    this.code = errorDetail.code;
    this.details = errorDetail.details;
    this.requestId = errorDetail.request_id;
  }
}

export interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export class HttpClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string = APP_CONFIG.apiBaseUrl) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  public async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { timeoutMs = 10000, headers, ...restOptions } = options;
    const url = `${this.baseUrl}${path.startsWith('/') ? path : `/${path}`}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...restOptions,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          ...headers,
        },
      });

      if (!response.ok) {
        let errorDetail: ApiErrorDetail = {
          code: `HTTP_${response.status}`,
          message: `Request failed with status ${response.status}`,
        };

        try {
          const body: ApiErrorResponse = await response.json();
          if (body?.error?.message) {
            errorDetail = body.error;
          }
        } catch {
          // Response body was not JSON
        }

        throw new ApiError(response.status, errorDetail);
      }

      // Check if response has content
      if (response.status === 204) {
        return {} as T;
      }

      return (await response.json()) as T;
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        throw err;
      }
      if (err instanceof Error && err.name === 'AbortError') {
        throw new ApiError(408, {
          code: 'REQUEST_TIMEOUT',
          message: `Request to ${path} timed out after ${timeoutMs}ms`,
        });
      }
      throw new ApiError(0, {
        code: 'NETWORK_ERROR',
        message: err instanceof Error ? err.message : 'Unknown network failure',
      });
    } finally {
      clearTimeout(timeoutId);
    }
  }

  public get<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: 'GET' });
  }

  public post<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }
}

export const httpClient = new HttpClient();
