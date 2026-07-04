from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"service": "Fraud Engine", "status": "running", "version": "1.0"})

@app.route("/score", methods=["POST"])
def score_fraud():
    data = request.json or {}
    invoice = data.get("invoice_data", {})
    vendor = data.get("vendor_data", {})
    
    score = 0
    indicators = []
    
    if not vendor.get("is_active", True):
        score += 60
        indicators.append("Vendor is marked as inactive or blacklisted.")
        
    if invoice.get("invoice_number") in vendor.get("historical_invoice_numbers", []):
        score += 70
        indicators.append("Duplicate invoice number detected for this vendor.")
        
    average_amount = vendor.get("average_invoice_amount", 0)
    gross_amount = invoice.get("gross_amount", 0)
    if average_amount > 0 and gross_amount > (average_amount * 3):
        score += 30
        indicators.append(f"Invoice amount ({gross_amount}) is significantly higher than historical average ({average_amount}).")
        
    if invoice.get("vendor_name", "").lower().strip() != vendor.get("vendor_name", "").lower().strip():
        score += 20
        indicators.append("Slight mismatch in vendor name compared to master data.")
        
    # Cap score at 100
    score = min(score, 100)
    
    # Classify risk level
    if score <= 20:
        risk_level = "LOW"
    elif score <= 50:
        risk_level = "MEDIUM"
    elif score <= 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
        
    return jsonify({
        "fraud_score": score,
        "risk_level": risk_level,
        "fraud_indicators": indicators
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
