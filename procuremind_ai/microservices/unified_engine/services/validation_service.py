import math

def validate_invoice(invoice_data, po_data, tolerance_percentage=0.02):
    discrepancies = []
    
    if not po_data:
        discrepancies.append("CRITICAL: Purchase Order not found in system.")
        return "Failed", discrepancies
        
    inv_vendor = (invoice_data.get("vendor_name") or "").lower().strip()
    po_vendor = (po_data.get("vendor_name") or "").lower().strip()
    
    # We may not have vendor_name in PO if it wasn't joined, check vendor_id as fallback
    if inv_vendor != po_vendor and po_vendor:
        discrepancies.append(f"HIGH: Vendor mismatch. Invoice: '{invoice_data.get('vendor_name')}', PO: '{po_data.get('vendor_name')}'")
        
    po_match = invoice_data.get("purchase_order_number") == po_data.get("po_number") and po_data.get("status") == "Approved"
    if not po_match:
        discrepancies.append(f"HIGH: PO mismatch or not approved.")
        
    # Math validation
    calculated_gross = invoice_data.get("net_amount", 0) + invoice_data.get("tax_amount", 0)
    if not math.isclose(calculated_gross, invoice_data.get("gross_amount", 0), rel_tol=0.001):
        discrepancies.append(f"HIGH: Invoice math error. Net + Tax != Gross")

    # PO Tolerance Validation (Header Level)
    variance = abs(invoice_data.get("gross_amount", 0) - po_data.get("total_amount", 0))
    allowed_variance = po_data.get("total_amount", 0) * float(tolerance_percentage)
    amount_match = variance <= allowed_variance
    
    if not amount_match:
        discrepancies.append(f"HIGH: Invoice total exceeds PO total beyond tolerance.")
    
    # Line Item Three-Way Matching
    po_lines = po_data.get("line_items", [])
    inv_lines = invoice_data.get("line_items", [])
    
    if po_lines and inv_lines:
        po_dict = {str(item.get('description', '')).lower().strip(): item for item in po_lines}
        
        for inv_item in inv_lines:
            desc = str(inv_item.get('description', '')).lower().strip()
            if desc not in po_dict:
                # If an item on the invoice isn't on the PO
                discrepancies.append(f"HIGH: Unknown item billed: '{inv_item.get('description')}' not found on PO.")
            else:
                # Match quantities and unit prices
                po_item = po_dict[desc]
                if float(inv_item.get('quantity', 0)) > float(po_item.get('quantity', 0)):
                    discrepancies.append(f"HIGH: Overbilled Quantity for '{inv_item.get('description')}'. PO allowed {po_item.get('quantity')}, billed {inv_item.get('quantity')}.")
                
                # Check unit price variance
                price_variance = abs(float(inv_item.get('unit_price', 0)) - float(po_item.get('unit_price', 0)))
                if price_variance > (float(po_item.get('unit_price', 0)) * float(tolerance_percentage)):
                    discrepancies.append(f"HIGH: Unit Price variance for '{inv_item.get('description')}'.")
        
    if any("CRITICAL" in d or "HIGH" in d for d in discrepancies):
        status = "Failed"
    elif any("LOW" in d or "MEDIUM" in d for d in discrepancies):
        status = "Warning"
    else:
        status = "Passed"
        
    return status, discrepancies
