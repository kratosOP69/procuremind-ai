# ProcureMind AI - Demo Video Script

Use this script as a guide when recording your 5-10 minute submission video.

## Preparation Before Recording
1. Start your local server (`start_services.bat`).
2. Have a sample Invoice PDF ready on your desktop (e.g. `sample_invoice.pdf`).
3. Have your OpenAI or Gemini API Key copied to your clipboard.
4. Open `http://127.0.0.1:8000` in your browser.

---

## 🎬 Introduction (1 min)
"Hi, my name is [Your Name], and this is my submission for the AI Engineer Round 3 Technical Assignment: AI Purchase Order Matching & Invoice Validation."

"Instead of relying entirely on no-code tools like n8n and Airtable, I decided to build a **Hybrid SaaS Application** using Python, Flask, and SQLite. This gives us full control over the UI, the matching algorithms, and the AI integrations."

---

## ⚙️ Step 1: Configuration & Master Data (1.5 mins)
1. **Click on 'AI Settings'**:
   - "First, the system is flexible. We can plug in any LLM provider. Let me paste my API key here and select my preferred model."
   - *(Paste key and click Save)*.
2. **Click on 'Master Data'**:
   - "Here we have our local replica of an ERP system. We can manage Vendors and Purchase Orders."
   - "Notice the Purchase Orders have **Line-Item capabilities**. This is a major architectural enhancement I made. We aren't just doing header-level totals; we are preparing the system for strict 3-way matching."
   - *(Show a PO by clicking Edit, highlighting the line items table)*.

---

## 🚀 Step 2: Invoice Processing & AI Extraction (2 mins)
1. **Click on 'Invoice Processing'**:
   - "Now let's process an incoming invoice."
   - *(Drag and drop your PDF/Image invoice into the upload zone)*.
   - "Behind the scenes, the system is converting this file, whether it's a PDF, JPG, Excel, or CSV, into text and passing it through our AI Extraction Prompt using OpenAI/Gemini."

---

## 🧠 Step 3: Explainable AI & Results (2 mins)
1. **Review the Results Screen**:
   - *(The screen will show APPROVED, REJECTED, or MANDATORY HUMAN REVIEW)*
   - "As you can see, the AI didn't just extract the data; it ran it through two custom Python microservices: a Validation Engine and a Fraud Engine."
   - **Scroll to Validation Engine**:
     - "The Validation Engine compared the extracted line items against the PO line items. It caught that the unit price was different." *(Point to a discrepancy if there is one)*.
   - **Scroll to Fraud Engine**:
     - "The Fraud Engine checked the vendor status and duplicate history. It assigned a Fraud Score."
   - **Explainable AI Reason**:
     - "Finally, a secondary LLM decision engine looked at all the discrepancies and generated this human-readable explanation for why the invoice was flagged."

---

## 📊 Step 4: Analytics Dashboard (1 min)
1. **Click on 'Analytics Dashboard'**:
   - "All this data flows back into a central dashboard for the finance team."
   - "We can see our KPIs update in real-time, and we have a full audit log of recent invoice ingestions."
   - *(Optional: Click 'View Details' on the recent invoice or demonstrate the Delete functionality)*.

---

## 🏁 Conclusion (30 secs)
"In conclusion, this architecture provides a scalable, secure, and highly intelligent solution for automated invoice processing. Thank you for your time, and I look forward to your feedback!"
