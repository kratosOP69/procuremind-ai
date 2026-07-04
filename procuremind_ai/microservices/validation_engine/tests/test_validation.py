import pytest
from src.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_successful_validation(client):
    payload = {
        "invoice_data": {
            "invoice_number": "INV-100",
            "vendor_name": "TechCorp",
            "purchase_order_number": "PO-500",
            "currency": "USD",
            "net_amount": 1000.0,
            "tax_amount": 100.0,
            "gross_amount": 1100.0,
            "line_items": []
        },
        "po_data": {
            "po_number": "PO-500",
            "vendor_name": "TechCorp",
            "total_amount": 1100.0,
            "currency": "USD",
            "status": "Approved"
        }
    }
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    data = response.json
    assert data["validation_status"] == "Passed"
    assert len(data["discrepancies"]) == 0

def test_missing_po(client):
    payload = {
        "invoice_data": {
            "invoice_number": "INV-101",
            "vendor_name": "TechCorp",
            "purchase_order_number": "PO-999",
            "currency": "USD",
            "net_amount": 1000.0,
            "tax_amount": 100.0,
            "gross_amount": 1100.0,
            "line_items": []
        },
        "po_data": None
    }
    response = client.post("/validate", json=payload)
    data = response.json
    assert data["validation_status"] == "Failed"
    assert "CRITICAL: Purchase Order not found in system." in data["discrepancies"]
