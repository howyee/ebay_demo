# ebay_demo (Python Flask + eBay API)
This is a simple full-stack project that connects to the **eBay Inventory API (Sandbox)** and displays product listings in a web interface.

It demonstrates how to integrate backend API calls with a frontend UI using Flask, HTML, CSS, and JavaScript.

---

## How It Works

The system uses a **two-step API flow**:

### 1. Get Inventory Items (SKU List)

The backend first calls:
GET /sell/inventory/v1/inventory_item

This returns a list of inventory items containing:
- SKU
- Basic product information

---

### 2. Get Offer Details for Each SKU

For each SKU, the backend calls:
GET /sell/inventory/v1/offer?sku={sku}


This returns:
- Price
- Currency
- Availability
- Offer-specific details

---

### 3. Merge Data

The backend combines both responses into a single JSON structure:

```json
{
  "sku": "123",
  "title": "Product Title",
  "description": "Product Description",
  "image": "image_url",
  "price": "10.00",
  "currency": "USD",
  "quantity": 5
}
