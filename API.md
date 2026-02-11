# PDF Maker API Documentation

REST API for generating PDF documents (invoices, proformas, purchase orders, and credit notes).

**Base URL:** `http://localhost:5002`

All values (item totals, tax totals, subtotals, grand totals, cargo values) must be precalculated by the caller. This service only formats and renders — it performs no arithmetic.

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pdf/invoice` | Generate an invoice PDF |
| POST | `/pdf/proforma` | Generate a proforma invoice PDF |
| POST | `/pdf/order` | Generate a purchase order PDF |
| POST | `/pdf/credit-note` | Generate a credit note PDF |

---

## Common Response

**Success (200):** Returns a PDF file as `application/pdf` attachment.

**Error (500):**
```json
{
  "error": "Error message"
}
```

**Bad Request (400):**
```json
{
  "error": "Invalid or missing JSON content"
}
```

---

## POST /pdf/invoice

Generate an invoice PDF document.

### Request Body

```json
{
  "filename": "invoice-001.pdf",
  "invoiceNumber": "INV-2024-001",
  "issuedDate": "2024-01-15T00:00:00Z",
  "customerReference": "PO-12345",
  "coordinates": { },
  "customer": { },
  "shipTo": { },
  "items": [ ],
  "paymentTerms": { },
  "shipping": { },
  "discount": { },
  "tax": [ ],
  "subTotal": 10000.00,
  "discountTotal": 500.00,
  "total": 9975.00,
  "totalQuantity": 1500.000,
  "cargoValues": { },
  "termsAndConditions": "Payment due within 30 days.",
  "bankDetails": "Bank Name: ABC Bank---Account: 123456789---SWIFT: ABCDEF"
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| filename | string | No | Output filename (default: `invoice.pdf`) |
| invoiceNumber | string | Yes | Invoice number |
| issuedDate | string | Yes | ISO 8601 date format |
| customerReference | string | No | Customer's reference number |
| coordinates | object | No | Company/sender contact details |
| customer | object | No | Bill-to contact details |
| shipTo | object | No | Ship-to contact details |
| items | array | No | Line items (with precalculated `total`) |
| paymentTerms | object | No | Payment terms and currency |
| shipping | object | No | Shipping details |
| discount | object | No | Discount information |
| tax | array | No | Tax items (with precalculated `total`) |
| subTotal | number | No | Subtotal before tax/discount |
| discountTotal | number | No | Total discount amount |
| total | number | No | Final total |
| totalQuantity | number | No | Total quantity/weight |
| cargoValues | object | No | Precalculated cargo values (FOB, freight, insurance, cargo) |
| termsAndConditions | string | No | Terms text (supports `\n` for line breaks) |
| bankDetails | string | No | Bank details (use `---` for line breaks) |

---

## POST /pdf/proforma

Generate a proforma invoice PDF document. Same structure as invoice.

### Request Body

```json
{
  "filename": "proforma-001.pdf",
  "proformaNumber": "PRO-2024-001",
  "issuedDate": "2024-01-15T00:00:00Z",
  "customerReference": "REF-12345",
  "coordinates": { },
  "customer": { },
  "shipTo": { },
  "items": [ ],
  "paymentTerms": { },
  "shipping": { },
  "discount": { },
  "tax": [ ],
  "subTotal": 10000.00,
  "discountTotal": 500.00,
  "total": 9975.00,
  "totalQuantity": 1500.000,
  "cargoValues": { },
  "termsAndConditions": "Valid for 30 days.",
  "bankDetails": "Bank Name: ABC Bank---Account: 123456789"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| proformaNumber | string | Yes | Proforma number |

*All other fields same as invoice.*

---

## POST /pdf/order

Generate a purchase order PDF document.

### Request Body

```json
{
  "filename": "order-001.pdf",
  "orderNumber": "PO-2024-001",
  "issuedDate": "2024-01-15T00:00:00Z",
  "supplierReference": "SUP-REF-001",
  "deliveryDate": "2024-02-15T00:00:00Z",
  "countryOfDischarge": "United States",
  "portOfDischarge": "Los Angeles",
  "coordinates": { },
  "supplier": { },
  "shipTo": { },
  "finalConsignee": { },
  "items": [ ],
  "paymentTerms": { },
  "discount": { },
  "tax": [ ],
  "subTotal": 10000.00,
  "discountTotal": 500.00,
  "total": 9975.00,
  "totalQuantity": 1500.000,
  "termsAndConditions": "Delivery terms apply."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| orderNumber | string | Yes | Purchase order number |
| supplierReference | string | No | Supplier's reference |
| deliveryDate | string | No | Expected delivery date (ISO 8601) |
| countryOfDischarge | string | No | Destination country |
| portOfDischarge | string | No | Destination port |
| supplier | object | No | Supplier contact details (labeled "Order To") |
| finalConsignee | object | No | Final consignee details |

---

## POST /pdf/credit-note

Generate a credit note PDF document.

### Request Body

```json
{
  "filename": "creditnote-001.pdf",
  "creditNoteNumber": "CN-2024-001",
  "issuedDate": "2024-01-15T00:00:00Z",
  "customerReference": "REF-001",
  "currency": "USD",
  "coordinates": { },
  "customer": { },
  "items": [ ],
  "total": 500.00,
  "relatedInvoice": {
    "invoiceNumber": "INV-2024-001",
    "issuedDate": "2024-01-01T00:00:00Z",
    "customerReference": "PO-12345",
    "total": 10000.00,
    "paymentTerms": {
      "currency": "USD"
    }
  },
  "termsAndConditions": "Credit applied to account."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| creditNoteNumber | string | Yes | Credit note number |
| currency | string | No | Currency code (default: `USD`) |
| total | number | No | Credit note total |
| relatedInvoice | object | No | Related invoice details |
| relatedInvoice.invoiceNumber | string | No | Original invoice number |
| relatedInvoice.issuedDate | string | No | Original invoice date (ISO 8601) |
| relatedInvoice.customerReference | string | No | Original customer reference |
| relatedInvoice.total | number | No | Original invoice total |
| relatedInvoice.paymentTerms.currency | string | No | Original invoice currency |

---

## Shared Object Schemas

### Contact Object

Used for `coordinates`, `customer`, `shipTo`, `supplier`, `finalConsignee`.

```json
{
  "name": "Company Name Inc.",
  "taxId": "TAX-123456",
  "address": "123 Main Street",
  "city": "New York",
  "province": "NY",
  "country": "USA",
  "zip": "10001",
  "email": "contact@company.com",
  "phone": "+1 555-123-4567",
  "others": ["Additional info line 1", "Additional info line 2"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| name | string | Contact/company name (required for display) |
| taxId | string | Tax identification number |
| address | string | Street address |
| city | string | City |
| province | string | State/province |
| country | string | Country |
| zip | string | Postal/ZIP code |
| email | string | Email address |
| phone | string | Phone number |
| others | array | Additional text lines |

---

### Item Object

Used for invoices, proformas, and purchase orders.

```json
{
  "product": {
    "name": "Product Name"
  },
  "description": "Detailed product description",
  "quantity": 100.5,
  "uom": "KG",
  "unitPrice": 15.00,
  "total": 1507.50
}
```

| Field | Type | Description |
|-------|------|-------------|
| product.name | string | Product name (displayed uppercase) |
| description | string | Item description |
| quantity | number | Quantity |
| uom | string | Unit of measure |
| unitPrice | number | Price per unit |
| total | number | Precalculated line total |

**Credit note items** only require `description`, `quantity`, `unitPrice`, and `total`.

---

### Payment Terms Object

```json
{
  "currency": "USD",
  "incoterms": "CIF",
  "incotermsDestination": "New York",
  "code": {
    "definition": "Net 30 Days"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| currency | string | Currency code (default: `USD`) |
| incoterms | string | Incoterms code (e.g., FOB, CIF, CIP, DDP) |
| incotermsDestination | string | Incoterms destination |
| code.definition | string | Payment terms description |

---

### Shipping Object

```json
{
  "bookingNumber": "BK-123456",
  "billOfLadingNumber": "BL-789012",
  "carrier": "Maersk Line",
  "vessel": "MSC Aurora",
  "voyageNumber": "V001",
  "ets": "2024-01-20T00:00:00Z",
  "eta": "2024-02-15T00:00:00Z",
  "portOfLoading": "Shanghai",
  "portOfDestination": "Los Angeles",
  "finalDestination": "Chicago",
  "cost": 1500.00
}
```

| Field | Type | Description |
|-------|------|-------------|
| bookingNumber | string | Booking reference number |
| billOfLadingNumber | string | Bill of lading number |
| carrier | string | Shipping carrier name |
| vessel | string | Vessel name |
| voyageNumber | string | Voyage number |
| ets | string | Estimated time of shipment (ISO 8601) |
| eta | string | Estimated time of arrival (ISO 8601) |
| portOfLoading | string | Origin port |
| portOfDestination | string | Destination port |
| finalDestination | string | Final delivery destination |
| cost | number | Freight cost |

---

### Cargo Values Object

Used in invoices and proformas. All values must be precalculated by the caller.

```json
{
  "fobValue": 10000.00,
  "freightValue": 2500.00,
  "insuranceValue": 25.00,
  "cargoValue": 12525.00
}
```

| Field | Type | Description |
|-------|------|-------------|
| fobValue | number | FOB value |
| freightValue | number | Freight cost |
| insuranceValue | number | Insurance value (row hidden if `0` or absent) |
| cargoValue | number | Total cargo value |

---

### Discount Object

```json
{
  "description": "Early Payment Discount"
}
```

| Field | Type | Description |
|-------|------|-------------|
| description | string | Discount description |

The `discountTotal` field in the main request body specifies the precalculated discount amount.

---

### Tax Object

```json
{
  "label": "VAT",
  "percentage": 10.0,
  "total": 1000.00
}
```

| Field | Type | Description |
|-------|------|-------------|
| label | string | Tax name/label |
| percentage | number | Tax percentage (displayed in label) |
| total | number | Precalculated tax amount |

---

## Example: Full Invoice Request

```json
{
  "filename": "invoice-2024-001.pdf",
  "invoiceNumber": "INV-2024-001",
  "issuedDate": "2024-01-15T00:00:00Z",
  "customerReference": "PO-CUST-123",
  "coordinates": {
    "name": "My Company Ltd.",
    "taxId": "US-123456789",
    "address": "456 Business Ave",
    "city": "Los Angeles",
    "province": "CA",
    "country": "USA",
    "zip": "90001",
    "email": "sales@mycompany.com",
    "phone": "+1 555-987-6543"
  },
  "customer": {
    "name": "Customer Corp.",
    "taxId": "CUST-TAX-001",
    "address": "789 Customer Blvd",
    "city": "Chicago",
    "province": "IL",
    "country": "USA",
    "zip": "60601",
    "email": "orders@customer.com"
  },
  "shipTo": {
    "name": "Customer Warehouse",
    "address": "100 Warehouse St",
    "city": "Chicago",
    "province": "IL",
    "country": "USA",
    "zip": "60602"
  },
  "items": [
    {
      "product": { "name": "Premium Coffee Beans" },
      "description": "Arabica Grade A, Origin: Colombia",
      "quantity": 500.000,
      "uom": "KG",
      "unitPrice": 15.00,
      "total": 7500.00
    },
    {
      "product": { "name": "Green Tea Leaves" },
      "description": "Organic, Origin: Japan",
      "quantity": 200.000,
      "uom": "KG",
      "unitPrice": 25.00,
      "total": 5000.00
    }
  ],
  "paymentTerms": {
    "currency": "USD",
    "incoterms": "CIF",
    "incotermsDestination": "Chicago",
    "code": {
      "definition": "Net 30 Days"
    }
  },
  "shipping": {
    "bookingNumber": "BK-2024-001",
    "billOfLadingNumber": "BL-2024-001",
    "carrier": "Hapag-Lloyd",
    "vessel": "Express Berlin",
    "voyageNumber": "V2024-01",
    "ets": "2024-01-25T00:00:00Z",
    "eta": "2024-02-20T00:00:00Z",
    "portOfLoading": "Cartagena",
    "portOfDestination": "Houston",
    "finalDestination": "Chicago",
    "cost": 2500.00
  },
  "tax": [
    { "label": "Sales Tax", "percentage": 8.25, "total": 1031.25 }
  ],
  "subTotal": 12500.00,
  "total": 13531.25,
  "totalQuantity": 700.000,
  "cargoValues": {
    "fobValue": 9975.00,
    "freightValue": 2500.00,
    "insuranceValue": 25.00,
    "cargoValue": 12500.00
  },
  "termsAndConditions": "1. Payment due within 30 days of invoice date.\n2. Late payments subject to 1.5% monthly interest.\n3. All disputes subject to California jurisdiction.",
  "bankDetails": "Bank: First National Bank---Account Name: My Company Ltd.---Account Number: 9876543210---Routing: 021000021---SWIFT: FNBKUS33"
}
```

### cURL Example

```bash
curl -X POST http://localhost:5002/pdf/invoice \
  -H "Content-Type: application/json" \
  -d @invoice-data.json \
  -o invoice.pdf
```

---

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

Server runs on port **5002** by default with debug mode enabled.

### Logs

- Console output: stdout
- Log file: `pdfmaker.log`
