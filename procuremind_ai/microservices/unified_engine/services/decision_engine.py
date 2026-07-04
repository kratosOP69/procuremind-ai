def generate_decision(val_status, fraud_score, confidence_score, is_duplicate):
    reason = []
    
    # Critical Fraud Indicators Check
    if is_duplicate:
        return "REJECTED", "Duplicate invoice detected."
        
    if fraud_score > 50:
        return "MANDATORY HUMAN REVIEW", f"High fraud risk detected (Score: {fraud_score})."
        
    if val_status == "Failed":
        return "MANDATORY HUMAN REVIEW", "Validation failed (Critical/High discrepancies)."
        
    if confidence_score < 85:
        return "MANDATORY HUMAN REVIEW", f"AI Confidence ({confidence_score}%) is below 85%."

    # Review Queue Check
    if 85 <= confidence_score <= 94:
        reason.append(f"AI Confidence is {confidence_score}%.")
        
    if 20 <= fraud_score <= 50:
        reason.append(f"Elevated fraud risk (Score: {fraud_score}).")
        
    if val_status == "Warning":
        reason.append("Validation returned warnings.")
        
    if reason:
        return "PROCUREMENT_REVIEW", " | ".join(reason)
        
    # Auto Processing Eligible
    if confidence_score >= 95 and fraud_score < 20 and val_status == "Passed":
        return "READY_FOR_PAYMENT", "All checks passed. High confidence."
        
    # Fallback
    return "PROCUREMENT_REVIEW", "Defaulted to review queue."
