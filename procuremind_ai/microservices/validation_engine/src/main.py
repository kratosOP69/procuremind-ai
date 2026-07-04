from flask import Flask, request, jsonify
import math

app = Flask(__name__)

TOLERANCE_PERCENTAGE = 0.02  # 2% tolerance

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"service": "Validation Engine", "status": "running", "version": "1.0"})

@app.route("/validate", methods=["POST"])
def validate_invoice():
    data = request.json or {}
    invoice = data.get("invoice_data", {})
    po = data.get("po_data")
    
    discrepancies = []
    
    if not po:
        discrepancies.append("CRITICAL: Purchase Order not found in system.")
        return jsonify({
            "vendor_match": False, "po_match": False, "currency_match": False, "amount_match": False,
            "validation_status": "Failed", "discrepancies": discrepancies
        })
        
    vendor_match = invoice.get("vendor_name", "").lower().strip() == po.get("vendor_name", "").lower().strip()
    if not vendor_match:
        discrepancies.append(f"HIGH: Vendor mismatch. Invoice: '{invoice.get('vendor_name')}', PO: '{po.get('vendor_name')}'")
        
    po_match = invoice.get("purchase_order_number") == po.get("po_number") and po.get("status") == "Approved"
    if not po_match:
        discrepancies.append(f"HIGH: PO mismatch or not approved. Status: {po.get('status')}")
        
    currency_match = invoice.get("currency") == po.get("currency")
    if not currency_match:
        discrepancies.append(f"HIGH: Currency mismatch. Invoice: {invoice.get('currency')}, PO: {po.get('currency')}")
        
    # Math validation
    calculated_gross = invoice.get("net_amount", 0) + invoice.get("tax_amount", 0)
    if not math.isclose(calculated_gross, invoice.get("gross_amount", 0), rel_tol=0.001):
        discrepancies.append(f"HIGH: Invoice math error. Net + Tax ({calculated_gross}) != Gross ({invoice.get('gross_amount')})")

    # PO Tolerance Validation
    variance = abs(invoice.get("gross_amount", 0) - po.get("total_amount", 0))
    allowed_variance = po.get("total_amount", 0) * TOLERANCE_PERCENTAGE
    amount_match = variance <= allowed_variance
    
    if not amount_match:
        discrepancies.append(f"HIGH: Invoice amount ({invoice.get('gross_amount')}) exceeds PO amount ({po.get('total_amount')}) beyond {TOLERANCE_PERCENTAGE*100}% tolerance.")
    elif variance > 0:
        discrepancies.append(f"LOW: Minor variance detected ({variance}), but within tolerance.")
        
    if any("CRITICAL" in d or "HIGH" in d for d in discrepancies):
        status = "Failed"
    elif any("LOW" in d or "MEDIUM" in d for d in discrepancies):
        status = "Warning"
    else:
        status = "Passed"
        
    return jsonify({
        "vendor_match": vendor_match,
        "po_match": po_match,
        "currency_match": currency_match,
        "amount_match": amount_match,
        "validation_status": status,
        "discrepancies": discrepancies
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
