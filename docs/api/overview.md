# API Reference Overview

This section provides detailed information about the API Credential service endpoints, authentication methods, and response formats.

## Base URL

The base URL for all API endpoints is:

```
https://api.karned.bzh/credential/
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
https://api.karned.bzh/credential/v1/
```

## Authentication

All API endpoints require authentication. The API Credential service supports the following authentication methods:

### Token Authentication

Most endpoints require a token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

### API Key Authentication

Some endpoints support License key authentication. Include the API key in the `X-License-Key` header:

```
X-License-Key: <your_license_key>
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

## Next Steps

- Visit our [Swagger Documentation](https://api.karned.bzh/credential/docs) for interactive API testing and exploration.
