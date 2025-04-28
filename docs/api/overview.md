# API Reference Overview

This section provides detailed information about the API Credential service endpoints, authentication methods, and response formats.

## Base URL

The base URL for all API endpoints is:

```
https://api.karned.com/credential/
```

For local development, the base URL is:

```
http://localhost:8000/
```

## API Versions

The API Credential service supports multiple API versions:

- **v0**: Legacy API (deprecated)
- **v1**: Current stable API

To specify the API version, include it in the URL path:

```
https://api.karned.com/credential/v1/
```

## Authentication

All API endpoints require authentication. The API Credential service supports the following authentication methods:

### Token Authentication

Most endpoints require a token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

### API Key Authentication

Some endpoints support API key authentication. Include the API key in the `X-API-Key` header:

```
X-API-Key: <your_api_key>
```

## Response Format

All API responses are in JSON format. A typical response has the following structure:

```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Responses

Error responses have the following structure:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message"
  }
}
```

## Rate Limiting

The API has rate limiting to prevent abuse. The current limits are:

- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

Rate limit information is included in the response headers:

- `X-RateLimit-Limit`: The maximum number of requests allowed per minute
- `X-RateLimit-Remaining`: The number of requests remaining in the current time window
- `X-RateLimit-Reset`: The time when the rate limit will reset (Unix timestamp)

## Next Steps

Explore the [Endpoints](endpoints.md) documentation for detailed information about each API endpoint.