# User Guide

Complete guide for using the Product Importer application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [CSV Upload](#csv-upload)
3. [Product Management](#product-management)
4. [Webhook Configuration](#webhook-configuration)
5. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### Accessing the Application

1. Start the application (see [QUICKSTART.md](../QUICKSTART.md))
2. Open your web browser
3. Navigate to: `http://localhost:8000`

### Interface Overview

The application has three main tabs:

1. **📤 Upload CSV** - Import products from CSV files
2. **📋 Products** - Manage your product catalog
3. **🔗 Webhooks** - Configure webhook notifications

---

## CSV Upload

### Preparing Your CSV File

Your CSV file must have the following structure:

```csv
name,sku,description
Product Name 1,SKU-001,This is a product description
Product Name 2,SKU-002,Another product description
Product Name 3,SKU-003,Yet another description
```

**Requirements:**
- **Header row required**: Must include `name`, `sku`, `description`
- **Required fields**: `name` and `sku` must have values
- **Optional field**: `description` can be empty
- **File size**: Maximum 500MB
- **File format**: CSV (comma-separated values)

**Important Notes:**
- SKU is case-insensitive (e.g., "PROD-001" and "prod-001" are treated as the same)
- Duplicate SKUs will overwrite existing products
- Empty rows are skipped
- Invalid rows are logged but don't stop the import

### Uploading a CSV File

1. **Navigate to Upload CSV tab**
   - Click on the "📤 Upload CSV" tab at the top

2. **Select your file**
   - Click "Choose File" button, OR
   - Drag and drop your CSV file into the upload area

3. **Monitor progress**
   - Progress bar shows percentage complete
   - Status messages indicate current stage:
     - "Parsing CSV file..."
     - "Validating data..."
     - "Importing products... (X/Y)"
     - "Import completed successfully!"

4. **Review results**
   - Success message appears when complete
   - Any errors are displayed in red below the progress bar
   - Check the Products tab to verify imported data

### Understanding Progress Updates

The progress indicator shows:

- **Progress Bar**: Visual percentage (0-100%)
- **Status Message**: Current operation being performed
- **Record Count**: "X/Y" shows processed vs total records
- **Errors**: Last 10 errors (if any) displayed below progress

### Handling Errors

If errors occur during import:

1. **Review error messages** - Each error shows the row number and issue
2. **Fix your CSV file** - Correct the problematic rows
3. **Re-upload** - Upload the corrected file (duplicates will be overwritten)

**Common Errors:**
- Missing SKU or name: Row will be skipped
- Invalid data format: Row will be skipped
- File too large: Reduce file size or split into multiple files

---

## Product Management

### Viewing Products

1. **Navigate to Products tab**
   - Click on the "📋 Products" tab

2. **Use filters** (optional)
   - **SKU**: Search by product SKU
   - **Name**: Search by product name
   - **Status**: Filter by Active/Inactive
   - **Description**: Search in descriptions

3. **Navigate pages**
   - Use "Previous" and "Next" buttons
   - Shows current page and total pages
   - 50 products per page

### Creating a Product

1. **Click "+ Add Product" button**
2. **Fill in the form:**
   - **SKU** (required): Unique product identifier
   - **Name** (required): Product name
   - **Description** (optional): Product description
   - **Active**: Checkbox to set active status
3. **Click "Save"**
4. Product appears in the list immediately

**Note:** SKU must be unique (case-insensitive). If a product with the same SKU exists, you'll get an error.

### Editing a Product

1. **Find the product** in the list
2. **Click "Edit" button** on the product row
3. **Modify fields** (SKU cannot be changed)
4. **Click "Save"**
5. Changes are saved immediately

### Deleting a Product

1. **Find the product** in the list
2. **Click "Delete" button** on the product row
3. **Confirm deletion** in the popup dialog
4. Product is removed immediately

### Bulk Delete All Products

**⚠️ Warning: This action cannot be undone!**

1. **Click "🗑️ Delete All" button** (top right of Products tab)
2. **Confirm** in the dialog: "Are you sure you want to delete ALL products?"
3. **Wait for completion** - Operation runs in background
4. **Success notification** appears when complete

---

## Webhook Configuration

### What are Webhooks?

Webhooks allow the application to send notifications to external URLs when events occur (e.g., product created, updated, or deleted).

### Creating a Webhook

1. **Navigate to Webhooks tab**
   - Click on the "🔗 Webhooks" tab

2. **Click "+ Add Webhook" button**

3. **Fill in the form:**
   - **URL**: The endpoint that will receive webhook notifications
     - Example: `https://example.com/api/webhooks`
     - Must be a valid HTTP/HTTPS URL
   - **Event Type**: Choose when to trigger
     - `product.created`: When a new product is created
     - `product.updated`: When a product is updated
     - `product.deleted`: When a product is deleted
   - **Enabled**: Toggle to enable/disable the webhook

4. **Click "Save"**
   - Webhook is now active (if enabled)

### Testing a Webhook

1. **Find the webhook** in the list
2. **Click "Test" button**
3. **View results:**
   - Success: Shows status code and response time
   - Failure: Shows error message

**Testing Tips:**
- Use services like [webhook.site](https://webhook.site) to test webhooks
- Check that your endpoint accepts POST requests
- Verify your endpoint returns a 2xx status code

### Enabling/Disabling Webhooks

1. **Find the webhook** in the list
2. **Toggle the switch** on the right
3. **Webhook status updates immediately**
   - Enabled: Webhook will trigger on events
   - Disabled: Webhook will not trigger

### Editing a Webhook

1. **Find the webhook** in the list
2. **Click "Edit" button**
3. **Modify fields** as needed
4. **Click "Save"**

### Deleting a Webhook

1. **Find the webhook** in the list
2. **Click "Delete" button**
3. **Confirm deletion**
4. Webhook is removed immediately

### Webhook Payload Format

When a webhook is triggered, your endpoint receives a POST request with:

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

**Event Types:**
- `product.created`: `data` contains `product_id` and `count`
- `product.updated`: `data` contains `product_id`
- `product.deleted`: `data` contains `product_id` and `count`

---

## Tips & Best Practices

### CSV Import

1. **Validate your CSV before uploading**
   - Check for required fields (name, sku)
   - Ensure SKUs are unique (case-insensitive)
   - Remove empty rows

2. **For large files (100,000+ records)**
   - Be patient - processing takes time
   - Monitor progress in real-time
   - Don't close the browser during import

3. **Handling duplicates**
   - Duplicate SKUs automatically overwrite existing products
   - Last import wins (newest data replaces old)

4. **Error handling**
   - Review error messages carefully
   - Fix errors and re-upload
   - Partial imports are saved (valid rows are imported)

### Product Management

1. **Use filters effectively**
   - Combine multiple filters for precise searches
   - Filters work together (AND logic)

2. **SKU best practices**
   - Use consistent SKU format
   - Keep SKUs short and meaningful
   - Remember: SKUs are case-insensitive

3. **Bulk operations**
   - Use bulk delete carefully
   - Consider exporting data before bulk delete
   - Operation cannot be undone

### Webhooks

1. **Testing webhooks**
   - Always test webhooks before production use
   - Use webhook.site or similar services for testing
   - Verify your endpoint handles POST requests

2. **Webhook reliability**
   - Webhooks are sent asynchronously
   - Failed webhooks don't block operations
   - Check webhook logs if notifications aren't received

3. **Security**
   - Use HTTPS URLs for webhooks
   - Implement authentication on your webhook endpoints
   - Validate webhook payloads

### Performance

1. **Large datasets**
   - Application handles up to 500,000 records
   - Processing time depends on file size
   - Progress updates every 1,000 records

2. **Browser recommendations**
   - Use modern browsers (Chrome, Firefox, Edge)
   - Keep browser tab open during imports
   - Don't navigate away during operations

---

## Troubleshooting

### Upload Issues

**Problem:** Upload not starting
- **Solution:** Check file size (max 500MB) and format (must be CSV)

**Problem:** Progress stuck
- **Solution:** Check Celery worker is running, refresh page

**Problem:** Import fails
- **Solution:** Review error messages, check CSV format

### Product Issues

**Problem:** Can't create product - "SKU already exists"
- **Solution:** SKU must be unique (case-insensitive). Use a different SKU or update existing product.

**Problem:** Products not showing
- **Solution:** Check filters, try clearing all filters

### Webhook Issues

**Problem:** Webhook test fails
- **Solution:** Check URL is accessible, endpoint accepts POST, returns 2xx status

**Problem:** Webhooks not triggering
- **Solution:** Verify webhook is enabled, check event type matches action

---

## Keyboard Shortcuts

Currently, no keyboard shortcuts are implemented. All operations use mouse/touch.

---

## Support

For technical issues or questions:
1. Check this user guide
2. Review [README.md](../README.md) for technical details
3. Check [API Documentation](API_DOCUMENTATION.md) for API usage

---

## Feature Requests

To request new features or report bugs, please contact your system administrator or development team.

