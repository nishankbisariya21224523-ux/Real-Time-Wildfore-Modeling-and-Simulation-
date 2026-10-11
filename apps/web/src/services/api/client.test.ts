import { describe, it, expect, vi, beforeEach } from 'vitest';
import { HttpClient, ApiError } from './client';

describe('HttpClient and RFC 7807 Problem Details Parsing', () => {
  const mockBaseUrl = 'http://test-api:8000/api/v1';
  let client: HttpClient;

  beforeEach(() => {
    client = new HttpClient(mockBaseUrl);
    vi.restoreAllMocks();
  });

  it('successfully returns JSON payload on 200 OK', async () => {
    const mockData = { id: 'reg-01', name: 'Uttarakhand' };
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockData,
      })
    );

    const result = await client.get('/regions');
    expect(result).toEqual(mockData);
  });

  it('parses structured RFC 7807 error responses on 4xx/5xx', async () => {
    const errorResponse = {
      error: {
        code: 'REGION_NOT_FOUND',
        message: 'The requested forest region was not found.',
        details: { region_id: 'unknown-id' },
        request_id: 'req-abc-123',
      },
    };

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => errorResponse,
      })
    );

    await expect(client.get('/regions/unknown-id')).rejects.toThrow(
      'The requested forest region was not found.'
    );

    try {
      await client.get('/regions/unknown-id');
    } catch (err: unknown) {
      expect(err).toBeInstanceOf(ApiError);
      const apiErr = err as ApiError;
      expect(apiErr.status).toBe(404);
      expect(apiErr.code).toBe('REGION_NOT_FOUND');
      expect(apiErr.requestId).toBe('req-abc-123');
      expect(apiErr.details).toEqual({ region_id: 'unknown-id' });
    }
  });

  it('handles network failure gracefully without crashing', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('Failed to connect to host'))
    );

    await expect(client.get('/health')).rejects.toThrow('Failed to connect to host');
  });
});
