# API Documentation

Complete API reference for the Product Importer application.

## Base URL

- Local: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

Currently, the API does not require authentication. For production use, implement authentication middleware.

---

## CSV Upload Endpoints

### Upload CSV File

Upload a CSV file for asynchronous processing.

**Endpoint:** `POST /api/upload`

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file` (required): CSV file (max 500MB)

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Upload started"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@products.csv"
```

**Status Codes:**
- `200 OK`: Upload started successfully
- `400 Bad Request`: Invalid file type or size exceeded
- `500 Internal Server Error`: Server error

---

### Get Upload Progress (Polling)

Get the current progress of an upload task.

**Endpoint:** `GET /api/upload/progress/{task_id}`

**Path Parameters:**
- `task_id` (string, required): Task ID returned from upload endpoint

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 0.65,
  "message": "Importing products... (325000/500000)",
  "total_records": 500000,
  "processed_records": 325000,
  "errors": null
}
```

**Status Values:**
- `pending`: Task is queued
- `processing`: Task is in progress
- `completed`: Task completed successfully
- `failed`: Task failed

**Example:**
```bash
curl "http://localhost:8000/api/upload/progress/550e8400-e29b-41d4-a716-446655440000"
```

---

### WebSocket Progress Updates

Real-time progress updates via WebSocket.

**Endpoint:** `WS /ws/progress/{task_id}`

**Path Parameters:**
- `task_id` (string, required): Task ID

**Message Format:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 0.65,
  "message": "Importing products... (325000/500000)",
  "total_records": 500000,
  "processed_records": 325000
}
```

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/progress/550e8400-e29b-41d4-a716-446655440000');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
};
```

---

## Product Endpoints

### List Products

Get a paginated list of products with optional filtering.

**Endpoint:** `GET /api/products`

**Query Parameters:**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 50): Number of records to return
- `sku` (string, optional): Filter by SKU (case-insensitive partial match)
- `name` (string, optional): Filter by name (case-insensitive partial match)
- `active` (boolean, optional): Filter by active status
- `description` (string, optional): Filter by description (case-insensitive partial match)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "sku": "PROD-001",
      "name": "Product Name",
      "description": "Product description",
      "active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 50,
  "total_pages": 25
}
```

**Example:**
```bash
curl "http://localhost:8000/api/products?skip=0&limit=50&active=true&sku=PROD"
```

---

### Get Single Product

Get a single product by ID.

**Endpoint:** `GET /api/products/{product_id}`

**Path Parameters:**
- `product_id` (UUID, required): Product ID

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "PROD-001",
  "name": "Product Name",
  "description": "Product description",
  "active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Product found
- `404 Not Found`: Product not found

**Example:**
```bash
curl "http://localhost:8000/api/products/550e8400-e29b-41d4-a716-446655440000"
```

---

### Create Product

Create a new product.

**Endpoint:** `POST /api/products`

**Request Body:**
```json
{
  "sku": "PROD-001",
  "name": "Product Name",
  "description": "Product description",
  "active": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "PROD-001",
  "name": "Product Name",
  "description": "Product description",
  "active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `201 Created`: Product created successfully
- `400 Bad Request`: Validation error or duplicate SKU

**Example:**
```bash
curl -X POST "http://localhost:8000/api/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-001",
    "name": "Product Name",
    "description": "Product description",
    "active": true
  }'
```

---

### Update Product

Update an existing product.

**Endpoint:** `PUT /api/products/{product_id}`

**Path Parameters:**
- `product_id` (UUID, required): Product ID

**Request Body:**
```json
{
  "name": "Updated Product Name",
  "description": "Updated description",
  "active": false
}
```

**Note:** SKU cannot be updated. Omit fields you don't want to change.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "PROD-001",
  "name": "Updated Product Name",
  "description": "Updated description",
  "active": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Product updated successfully
- `404 Not Found`: Product not found

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/products/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product Name",
    "active": false
  }'
```

---

### Delete Product

Delete a single product.

**Endpoint:** `DELETE /api/products/{product_id}`

**Path Parameters:**
- `product_id` (UUID, required): Product ID

**Response:**
- `204 No Content`: Product deleted successfully
- `404 Not Found`: Product not found

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/products/550e8400-e29b-41d4-a716-446655440000"
```

---

### Bulk Delete Products

Delete all products from the database.

**Endpoint:** `DELETE /api/products`

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Bulk delete started"
}
```

**Status Codes:**
- `200 OK`: Bulk delete task started

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/products"
```

---

### Get Bulk Delete Status

Get the status of a bulk delete operation.

**Endpoint:** `GET /api/products/bulk-delete/status/{task_id}`

**Path Parameters:**
- `task_id` (string, required): Task ID from bulk delete

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 1.0,
  "message": "Deleted 1250 products successfully.",
  "deleted_count": 1250
}
```

**Example:**
```bash
curl "http://localhost:8000/api/products/bulk-delete/status/550e8400-e29b-41d4-a716-446655440000"
```

---

## Webhook Endpoints

### List Webhooks

Get all configured webhooks.

**Endpoint:** `GET /api/webhooks`

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://example.com/webhook",
    "event_type": "product.created",
    "enabled": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/webhooks"
```

---

### Get Single Webhook

Get a single webhook by ID.

**Endpoint:** `GET /api/webhooks/{webhook_id}`

**Path Parameters:**
- `webhook_id` (UUID, required): Webhook ID

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://example.com/webhook",
  "event_type": "product.created",
  "enabled": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/webhooks/550e8400-e29b-41d4-a716-446655440000"
```

---

### Create Webhook

Create a new webhook.

**Endpoint:** `POST /api/webhooks`

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "event_type": "product.created",
  "enabled": true
}
```

**Event Types:**
- `product.created`: Triggered when a product is created
- `product.updated`: Triggered when a product is updated
- `product.deleted`: Triggered when a product is deleted

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://example.com/webhook",
  "event_type": "product.created",
  "enabled": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/webhooks" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "event_type": "product.created",
    "enabled": true
  }'
```

---

### Update Webhook

Update an existing webhook.

**Endpoint:** `PUT /api/webhooks/{webhook_id}`

**Path Parameters:**
- `webhook_id` (UUID, required): Webhook ID

**Request Body:**
```json
{
  "url": "https://new-url.com/webhook",
  "event_type": "product.updated",
  "enabled": false
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://new-url.com/webhook",
  "event_type": "product.updated",
  "enabled": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/webhooks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

---

### Delete Webhook

Delete a webhook.

**Endpoint:** `DELETE /api/webhooks/{webhook_id}`

**Path Parameters:**
- `webhook_id` (UUID, required): Webhook ID

**Response:**
- `204 No Content`: Webhook deleted successfully
- `404 Not Found`: Webhook not found

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/webhooks/550e8400-e29b-41d4-a716-446655440000"
```

---

### Test Webhook

Send a test event to a webhook.

**Endpoint:** `POST /api/webhooks/{webhook_id}/test`

**Path Parameters:**
- `webhook_id` (UUID, required): Webhook ID

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "response_time_ms": 45.2,
  "error": null
}
```

**Status Codes:**
- `200 OK`: Test completed (check `success` field for result)
- `404 Not Found`: Webhook not found

**Example:**
```bash
curl -X POST "http://localhost:8000/api/webhooks/550e8400-e29b-41d4-a716-446655440000/test"
```

---

## Webhook Payload Format

When webhooks are triggered, they receive POST requests with the following format:

```json
{
  "event_type": "product.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "count": 1
  }
}
```

**Event Types and Data:**

- `product.created`: `{"product_id": "...", "count": 1}`
- `product.updated`: `{"product_id": "..."}`
- `product.deleted`: `{"product_id": "...", "count": 1}`

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

**Common Status Codes:**
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production, implement rate limiting middleware.

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- View all endpoints
- Test API calls directly
- See request/response schemas
- Understand data models

