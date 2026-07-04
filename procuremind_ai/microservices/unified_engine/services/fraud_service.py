def score_fraud(invoice_data, vendor_data, is_duplicate=False):
    score = 0
    indicators = []
    
    if not vendor_data.get("is_active", True):
        score += 60
        indicators.append("Vendor is marked as inactive or blacklisted.")
        
    if is_duplicate:
        score += 70
        indicators.append("Duplicate invoice number detected for this vendor.")
        
    average_amount = vendor_data.get("average_invoice_amount", 0)
    gross_amount = invoice_data.get("gross_amount", 0)
    if average_amount > 0 and gross_amount > (average_amount * 3):
        score += 30
        indicators.append(f"Invoice amount (${gross_amount}) is significantly higher than historical average (${average_amount}).")
        
    score = min(score, 100)
    
    if score <= 20:
        risk_level = "LOW"
    elif score <= 50:
        risk_level = "MEDIUM"
    elif score <= 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
        
    return score, risk_level, indicators
