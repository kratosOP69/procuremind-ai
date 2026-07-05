import json
import base64
import PyPDF2
from openai import OpenAI
from database.db import get_setting

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_invoice_data(file_path):
    provider = get_setting('ai_provider', 'openai')
    api_key = get_setting('openai_api_key') if provider == 'openai' else get_setting('gemini_api_key')
    model = get_setting('ai_model', 'gpt-4o') if provider == 'openai' else get_setting('gemini_model', 'gemini-1.5-flash')
    
    if not api_key:
        # Mock Response if no API key is provided
        return {
            "vendor_name": "Stark Industries",
            "vendor_id": "V-100",
            "po_number": "PO-123",
            "invoice_number": "INV-PO123-001",
            "invoice_date": "2026-07-04",
            "due_date": "2026-08-04",
            "currency": "USD",
            "net_amount": 200000.0,
            "tax_amount": 0.0,
            "gross_amount": 200000.0,
            "line_items": [{"description": "Water Bottles", "quantity": 200.0, "unit_price": 1000.0, "total": 200000.0}],
            "confidence_score": 96,
            "extraction_warnings": [f"Mock data used. Please add {provider.upper()} API key."]
        }

    system_prompt = """
    You are an expert OCR and Document AI extraction system for ProcureMind AI.
    Extract the following fields from the invoice document. 
    Return strictly as a JSON object matching this schema:
    {
        "vendor_name": "str",
        "vendor_id": "str or null",
        "po_number": "str",
        "invoice_number": "str",
        "invoice_date": "YYYY-MM-DD",
        "due_date": "YYYY-MM-DD",
        "currency": "str",
        "net_amount": float,
        "tax_amount": float,
        "gross_amount": float,
        "line_items": [{"description": "str", "quantity": float, "unit_price": float, "total": float}],
        "confidence_score": int (0-100 based on legibility),
        "extraction_warnings": ["str"] (list any issues reading the document)
    }
    """

    ext = file_path.lower().split('.')[-1]

    if provider == 'openai':
        client = OpenAI(api_key=api_key)
        messages = [{"role": "system", "content": system_prompt}]
        
        if ext == 'pdf':
            text_content = extract_text_from_pdf(file_path)
            messages.append({"role": "user", "content": f"Extract data from this invoice text:\n\n{text_content}"})
        elif ext in ['jpg', 'jpeg', 'png']:
            base64_image = encode_image(file_path)
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract data from this invoice image:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/{ext};base64,{base64_image}"}}
                ]
            })
        else:
            # Gracefully handle all other types (csv, docx, txt, etc.) by trying to read as text
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read(5000) # Read first 5000 chars
                messages.append({"role": "user", "content": f"Extract data from this {ext} file text:\n\n{text_content}"})
            except Exception:
                messages.append({"role": "user", "content": f"Extract data. File is {ext}, contents could not be parsed."})

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={ "type": "json_object" },
                temperature=0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"confidence_score": 0, "extraction_warnings": [f"OpenAI API Error: {str(e)}"], "gross_amount": 0}

    elif provider == 'gemini':
        import urllib.request
        import urllib.error
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        parts = [{"text": system_prompt + "\n\nExtract data from this document:"}]
        if ext == 'pdf':
            text_content = extract_text_from_pdf(file_path)
            parts.append({"text": text_content})
        elif ext in ['jpg', 'jpeg', 'png']:
            base64_image = encode_image(file_path)
            mime_type = "image/jpeg" if ext in ['jpg', 'jpeg'] else "image/png"
            parts.append({"inlineData": {"mimeType": mime_type, "data": base64_image}})
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read(5000)
                parts.append({"text": f"File type: {ext}\n\n" + text_content})
            except Exception:
                parts.append({"text": f"File type: {ext}. Contents could not be read."})
            
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.0}
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                return json.loads(result['candidates'][0]['content']['parts'][0]['text'])
        except urllib.error.HTTPError as e:
            return {"confidence_score": 0, "extraction_warnings": [f"Gemini API HTTP Error: {e.read().decode()}"], "gross_amount": 0}
        except Exception as e:
            return {"confidence_score": 0, "extraction_warnings": [f"Gemini API Error: {str(e)}"], "gross_amount": 0}
