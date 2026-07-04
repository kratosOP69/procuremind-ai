from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import sqlite3
from datetime import datetime

from database.db import get_db, init_db, log_audit, get_setting, set_setting
from services.validation_service import validate_invoice
from services.fraud_service import score_fraud
from services.decision_engine import generate_decision
from services.ai_service import extract_invoice_data

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------------------------------
# FILE SERVING
# ----------------------------------------------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ----------------------------------------------------
# UI ROUTES
# ----------------------------------------------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/invoice_viewer")
def invoice_viewer():
    return render_template("invoice_viewer.html")

@app.route("/master_data")
def master_data():
    return render_template("master_data.html")

@app.route("/settings")
def settings_page():
    return render_template("settings.html")

# ----------------------------------------------------
# CORE MICROSERVICE APIS (PRESERVED)
# ----------------------------------------------------
@app.route("/validate", methods=["POST"])
def validate_api():
    data = request.json or {}
    inv = data.get("invoice_data", {})
    po = data.get("po_data")
    tol = float(get_setting('tolerance_percentage', 0.02))
    status, disc = validate_invoice(inv, po, tol)
    return jsonify({"validation_status": status, "discrepancies": disc})

@app.route("/score", methods=["POST"])
def score_api():
    data = request.json or {}
    inv = data.get("invoice_data", {})
    ven = data.get("vendor_data", {})
    dup = data.get("is_duplicate", False)
    score, risk, ind = score_fraud(inv, ven, dup)
    return jsonify({"fraud_score": score, "risk_level": risk, "fraud_indicators": ind})

@app.route("/decision", methods=["POST"])
def decision_api():
    data = request.json or {}
    status = data.get("validation_status")
    score = data.get("fraud_score")
    conf = data.get("confidence_score")
    dup = data.get("is_duplicate", False)
    
    decision, reason = generate_decision(status, score, conf, dup)
    return jsonify({"decision": decision, "reason": reason})

# ----------------------------------------------------
# ORCHESTRATION & UPLOAD API
# ----------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    log_audit("Unknown", "Upload", f"Uploaded file: {file.filename}")
    
    # 1. AI Extraction
    extracted_data = extract_invoice_data(filepath)
    inv_num = extracted_data.get('invoice_number', 'UNKNOWN')
    ven_name = extracted_data.get('vendor_name', 'UNKNOWN')
    po_num = extracted_data.get('po_number', '')
    conf = extracted_data.get('confidence_score', 0)
    
    log_audit(inv_num, "Extraction Completed", f"Confidence: {conf}%")
    
    conn = get_db()
    c = conn.cursor()
    
    # 2. Duplicate Check
    c.execute("SELECT COUNT(*) FROM invoices WHERE invoice_number = ?", (inv_num,))
    is_duplicate = c.fetchone()[0] > 0
    
    # 3. Fetch Master Data
    c.execute("SELECT * FROM purchase_orders WHERE po_number = ?", (po_num,))
    po_row = c.fetchone()
    po_data = dict(po_row) if po_row else None
    
    if po_data:
        c.execute("SELECT * FROM po_line_items WHERE po_number = ?", (po_num,))
        po_data['line_items'] = [dict(row) for row in c.fetchall()]
    
    c.execute("SELECT * FROM vendors WHERE vendor_name = ? OR vendor_id = ?", (ven_name, extracted_data.get('vendor_id', '')))
    ven_row = c.fetchone()
    
    if not ven_row:
        # Auto-create missing vendor with HIGH risk for review
        new_ven_id = extracted_data.get('vendor_id') or f"V-UNKNOWN-{inv_num}"
        c.execute(
            "INSERT INTO vendors (vendor_id, vendor_name, risk_level, country, is_active) VALUES (?, ?, ?, ?, ?)",
            (new_ven_id, ven_name, 'HIGH', 'Unknown', 0)
        )
        conn.commit()
        ven_data = {'vendor_id': new_ven_id, 'vendor_name': ven_name, 'risk_level': 'HIGH', 'is_active': 0}
        log_audit(inv_num, "System", f"Auto-created missing vendor: {ven_name}")
    else:
        ven_data = dict(ven_row)
    
    conn.close()
    
    # 4. Run Microservices
    val_status, val_disc = validate_invoice(extracted_data, po_data, float(get_setting('tolerance_percentage', 0.02)))
    log_audit(inv_num, "Validation Completed", val_status)
    
    fraud_score, risk_level, fraud_ind = score_fraud(extracted_data, ven_data, is_duplicate)
    log_audit(inv_num, "Fraud Analysis Completed", f"Score: {fraud_score}")
    
    decision, reason = generate_decision(val_status, fraud_score, conf, is_duplicate)
    log_audit(inv_num, "Decision Generated", decision)
    
    # 5. Save to DB
    conn = get_db()
    c = conn.cursor()
    import json
    c.execute(
        "INSERT OR REPLACE INTO invoices (invoice_number, vendor_id, po_number, gross_amount, currency, status, created_at, file_name, extracted_data, validation_results, fraud_results) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            inv_num, ven_data.get('vendor_id', 'Unknown'), po_num, extracted_data.get('gross_amount'), extracted_data.get('currency'), decision, datetime.now().isoformat(),
            file.filename,
            json.dumps(extracted_data),
            json.dumps({"status": val_status, "discrepancies": val_disc}),
            json.dumps({"score": fraud_score, "risk_level": risk_level, "indicators": fraud_ind, "is_duplicate": is_duplicate})
        )
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        "extraction": extracted_data,
        "validation": {"status": val_status, "discrepancies": val_disc},
        "fraud": {"score": fraud_score, "risk_level": risk_level, "indicators": fraud_ind, "is_duplicate": is_duplicate},
        "decision": {"status": decision, "reason": reason}
    })

@app.route("/api/invoices/<invoice_number>/override", methods=["POST"])
def override_invoice(invoice_number):
    data = request.json
    new_status = data.get("status")
    
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE invoices SET status = ? WHERE invoice_number = ?", (new_status, invoice_number))
    conn.commit()
    conn.close()
    
    log_audit(invoice_number, f"Human Override: {new_status}", "Actioned from dashboard", "Admin")
    return jsonify({"success": True})

# ----------------------------------------------------
# DB CRUD APIS
# ----------------------------------------------------
@app.route("/api/vendors", methods=["GET", "POST"])
def manage_vendors():
    conn = get_db()
    if request.method == "POST":
        data = request.json
        conn.execute(
            "INSERT OR REPLACE INTO vendors (vendor_id, vendor_name, country, risk_level, payment_terms, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            (data['vendor_id'], data['vendor_name'], data.get('country', 'US'), data.get('risk_level', 'LOW'), data.get('payment_terms', 'Net 30'), data.get('is_active', 1))
        )
        conn.commit()
        return jsonify({"success": True})
    
    vendors = [dict(row) for row in conn.execute("SELECT * FROM vendors").fetchall()]
    conn.close()
    return jsonify(vendors)

@app.route("/api/vendors/<vendor_id>", methods=["DELETE"])
def delete_vendor(vendor_id):
    conn = get_db()
    conn.execute("DELETE FROM vendors WHERE vendor_id = ?", (vendor_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/pos", methods=["GET", "POST", "PUT"])
def manage_pos():
    conn = get_db()
    c = conn.cursor()
    if request.method == "POST":
        data = request.json
        created_at = data.get('created_at', datetime.now().isoformat())
        
        c.execute("INSERT OR REPLACE INTO purchase_orders (po_number, vendor_id, total_amount, currency, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (data['po_number'], data['vendor_id'], data['total_amount'], data['currency'], data['status'], created_at))
        
        # Clear and insert line items
        c.execute("DELETE FROM po_line_items WHERE po_number = ?", (data['po_number'],))
        line_items = data.get('line_items', [])
        for item in line_items:
            c.execute("INSERT INTO po_line_items (po_number, description, quantity, unit_price, total) VALUES (?, ?, ?, ?, ?)",
                      (data['po_number'], item.get('description'), item.get('quantity'), item.get('unit_price'), item.get('total')))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})
        
    c.execute("""
        SELECT p.*, v.vendor_name 
        FROM purchase_orders p 
        LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
    """)
    pos = [dict(row) for row in c.fetchall()]
    
    for po in pos:
        c.execute("SELECT * FROM po_line_items WHERE po_number = ?", (po['po_number'],))
        po['line_items'] = [dict(row) for row in c.fetchall()]
        
    conn.close()
    return jsonify(pos)

@app.route("/api/pos/<po_number>", methods=["DELETE"])
def delete_po(po_number):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM purchase_orders WHERE po_number = ?", (po_number,))
    c.execute("DELETE FROM po_line_items WHERE po_number = ?", (po_number,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/invoices", methods=["GET"])
def get_invoices():
    conn = get_db()
    invoices = [dict(row) for row in conn.execute("SELECT * FROM invoices ORDER BY created_at DESC").fetchall()]
    conn.close()
    return jsonify(invoices)

@app.route("/api/invoices/<invoice_number>", methods=["GET", "DELETE"])
def get_invoice(invoice_number):
    conn = get_db()
    c = conn.cursor()
    
    if request.method == "DELETE":
        c.execute("DELETE FROM invoices WHERE invoice_number = ?", (invoice_number,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
        
    c.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM invoices")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'READY_FOR_PAYMENT' OR status = 'APPROVED'")
    approved = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'PROCUREMENT_REVIEW' OR status = 'MANDATORY HUMAN REVIEW'")
    review = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'REJECTED'")
    rejected = c.fetchone()[0]
    
    conn.close()
    return jsonify({
        "total": total,
        "approved": approved,
        "review": review,
        "rejected": rejected
    })

@app.route("/api/settings", methods=["GET", "POST"])
def manage_settings():
    if request.method == "POST":
        data = request.json
        for key in ['ai_provider', 'openai_api_key', 'ai_model', 'gemini_api_key', 'gemini_model', 'tolerance_percentage', 'fraud_critical_threshold']:
            if key in data:
                set_setting(key, data[key])
        return jsonify({"success": True})
    
    return jsonify({
        "ai_provider": get_setting('ai_provider', 'openai'),
        "openai_api_key": get_setting('openai_api_key', ''),
        "ai_model": get_setting('ai_model', 'gpt-4o'),
        "gemini_api_key": get_setting('gemini_api_key', ''),
        "gemini_model": get_setting('gemini_model', 'gemini-1.5-flash'),
        "tolerance_percentage": get_setting('tolerance_percentage', '0.02'),
        "fraud_critical_threshold": get_setting('fraud_critical_threshold', '50')
    })

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=8000)
