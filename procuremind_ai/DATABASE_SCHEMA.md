# Database Schema

ProcureMind AI uses a local SQLite database (`procuremind.db`) generated automatically upon starting the Flask application. It consists of the following tables.

## 1. `vendors`
Stores the master data of all vendors interacting with the organization.
- `vendor_id` (TEXT, Primary Key)
- `vendor_name` (TEXT)
- `risk_level` (TEXT) - `LOW`, `MEDIUM`, or `HIGH`
- `country` (TEXT)
- `payment_terms` (TEXT)
- `is_active` (INTEGER) - 1 (Active) or 0 (Inactive/Blacklisted)

## 2. `purchase_orders`
Stores the header-level information of Purchase Orders issued to vendors.
- `po_number` (TEXT, Primary Key)
- `vendor_id` (TEXT) - Foreign Key to `vendors`
- `total_amount` (REAL)
- `currency` (TEXT)
- `status` (TEXT) - e.g., `Approved`, `Pending`
- `created_at` (TEXT)

## 3. `po_line_items`
Stores the line-item level details of Purchase Orders, allowing for strict 3-way matching.
- `id` (INTEGER, Primary Key)
- `po_number` (TEXT) - Foreign Key to `purchase_orders` (Cascades on delete)
- `description` (TEXT) - Name of the item/service
- `quantity` (REAL)
- `unit_price` (REAL)
- `total` (REAL) - quantity * unit_price

## 4. `invoices`
Stores the historical record of all processed invoices and their AI-determined validation outcomes.
- `invoice_number` (TEXT, Primary Key)
- `vendor_id` (TEXT) - Foreign Key to `vendors`
- `po_number` (TEXT)
- `gross_amount` (REAL)
- `currency` (TEXT)
- `status` (TEXT) - e.g., `Passed`, `Failed`, `Warning`
- `created_at` (TEXT)
- `file_name` (TEXT)
- `extracted_data` (TEXT) - JSON dump of the AI OCR extraction
- `validation_results` (TEXT) - JSON dump of the discrepancies found
- `fraud_results` (TEXT) - JSON dump of the fraud score and indicators

## 5. `audit_logs`
Tracks major events within the system for compliance and debugging.
- `id` (INTEGER, Primary Key)
- `action` (TEXT)
- `timestamp` (TEXT)
- `details` (TEXT)

## 6. `settings`
Stores user configurations and global parameters.
- `key` (TEXT, Primary Key)
- `value` (TEXT)
