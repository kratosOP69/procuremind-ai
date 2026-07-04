import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "procuremind.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Vendors Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id TEXT PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            risk_level TEXT,
            country TEXT,
            currency TEXT,
            payment_terms TEXT,
            preferred_flag BOOLEAN DEFAULT 0,
            approved_iban TEXT,
            average_invoice_amount REAL DEFAULT 0
        )
    """)

    # Purchase Orders Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            po_number TEXT PRIMARY KEY,
            vendor_id TEXT,
            vendor_name TEXT,
            total_amount REAL,
            currency TEXT,
            status TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
        )
    """)

    # PO Line Items
    c.execute("""
        CREATE TABLE IF NOT EXISTS po_line_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT,
            description TEXT,
            quantity REAL,
            unit_price REAL,
            total REAL,
            FOREIGN KEY (po_number) REFERENCES purchase_orders(po_number) ON DELETE CASCADE
        )
    """)

    # Invoices Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_number TEXT PRIMARY KEY,
            vendor_id TEXT,
            po_number TEXT,
            gross_amount REAL,
            currency TEXT,
            status TEXT,
            created_at TIMESTAMP,
            file_name TEXT,
            extracted_data TEXT,
            validation_results TEXT,
            fraud_results TEXT,
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
            FOREIGN KEY (po_number) REFERENCES purchase_orders(po_number)
        )
    """)

    # Audit Logs
    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            action TEXT,
            timestamp TIMESTAMP,
            details TEXT,
            user_override TEXT
        )
    """)

    # Settings
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    seed_db(conn)
    conn.close()

def seed_db(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM settings")
    if c.fetchone()[0] == 0:
        # Initialize default settings
        c.execute("INSERT INTO settings (key, value) VALUES ('openai_api_key', '')")
        c.execute("INSERT INTO settings (key, value) VALUES ('tolerance_percentage', '0.02')")
        c.execute("INSERT INTO settings (key, value) VALUES ('fraud_critical_threshold', '50')")
        c.execute("INSERT INTO settings (key, value) VALUES ('ai_model', 'gpt-4o')")
        conn.commit()

def log_audit(invoice_number, action, details="", user_override="System"):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_logs (invoice_number, action, timestamp, details, user_override) VALUES (?, ?, ?, ?, ?)",
        (invoice_number, action, datetime.now().isoformat(), details, user_override)
    )
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row['value'] if row else default

def set_setting(key, value):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
