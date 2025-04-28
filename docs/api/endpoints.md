# API Endpoints

This page documents all available endpoints in the API Credential service.

## Authentication Endpoints

### Get Token

```
POST /v1/token
```

Generates a new authentication token.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "token": "string",
    "expires_at": "datetime",
    "token_type": "bearer"
  }
}
```

### Refresh Token

```
POST /v1/token/refresh
```

Refreshes an existing authentication token.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "token": "string",
    "expires_at": "datetime",
    "token_type": "bearer"
  }
}
```

### Revoke Token

```
POST /v1/token/revoke
```

Revokes an existing authentication token.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "status": "success",
  "message": "Token revoked successfully"
}
```

## Credential Management Endpoints

### List Credentials

```
GET /v1/credentials
```

Returns a list of all credentials for the authenticated user.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "credentials": [
      {
        "id": "string",
        "name": "string",
        "type": "string",
        "created_at": "datetime",
        "last_used": "datetime"
      }
    ]
  }
}
```

### Create Credential

```
POST /v1/credentials
```

Creates a new credential.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Request Body:**

```json
{
  "name": "string",
  "type": "string",
  "permissions": ["string"]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "credential": {
      "id": "string",
      "name": "string",
      "type": "string",
      "key": "string",
      "created_at": "datetime"
    }
  },
  "message": "Credential created successfully"
}
```

### Get Credential

```
GET /v1/credentials/{credential_id}
```

Returns details for a specific credential.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "credential": {
      "id": "string",
      "name": "string",
      "type": "string",
      "created_at": "datetime",
      "last_used": "datetime",
      "permissions": ["string"]
    }
  }
}
```

### Update Credential

```
PUT /v1/credentials/{credential_id}
```

Updates an existing credential.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Request Body:**

```json
{
  "name": "string",
  "permissions": ["string"]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "credential": {
      "id": "string",
      "name": "string",
      "type": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  },
  "message": "Credential updated successfully"
}
```

### Delete Credential

```
DELETE /v1/credentials/{credential_id}
```

Deletes an existing credential.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "status": "success",
  "message": "Credential deleted successfully"
}
```

## Permission Endpoints

### List Permissions

```
GET /v1/permissions
```

Returns a list of all available permissions.

**Request Headers:**

```
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "permissions": [
      {
        "id": "string",
        "name": "string",
        "description": "string"
      }
    ]
  }
}
```

## Health Check Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API.

**Response:**

```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "version": "string",
    "uptime": "string"
  }
}
```