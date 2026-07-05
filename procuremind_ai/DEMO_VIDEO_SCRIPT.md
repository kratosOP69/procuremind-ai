# ProcureMind AI - Demo Video Script

Use this script as a guide when recording your 5-10 minute submission video.

## Preparation Before Recording
1. Start your local server (`start_services.bat`).
2. Have your `Water Bottles` Invoice PDF ready on your desktop.
3. Ensure that in the **Master Data** tab, `PO-123` has the line item explicitly set to exactly `Water Bottles` with Qty 200 and Price 1000.
4. Open `http://127.0.0.1:8000` in your browser.

---

## 🎬 Introduction (1 min)
"Hi, my name is [Your Name], and this is my submission for the AI Engineer Round 3 Technical Assignment: AI Purchase Order Matching & Invoice Validation."

"Instead of relying entirely on no-code tools like n8n and Airtable, I decided to build a **Hybrid SaaS Application** using Python, Flask, and SQLite. This gives us full control over the UI, the 3-way matching algorithms, and the AI integrations."

---

## ⚙️ Step 1: Configuration & Master Data (1.5 mins)
1. **Click on 'AI Settings'**:
   - "First, the system is flexible. We can plug in any LLM provider like OpenAI or Gemini. Let me select my preferred model."
2. **Click on 'Master Data'**:
   - "Here we have our local replica of an ERP system. We can manage Vendors and Purchase Orders."
   - "Notice the Purchase Orders have **Line-Item capabilities**. This is a major architectural enhancement I made. We aren't just doing header-level totals; we are preparing the system for strict 3-way matching."
   - *(Click Edit on PO-123 to show the 'Water Bottles' line item)*.
   - "For example, here is PO-123 for our vendor Stark Industries, explicitly approved for 200 Water Bottles."

---

## 🚀 Step 2: Invoice Processing & AI Extraction (2 mins)
1. **Click on 'Invoice Processing'**:
   - "Now let's process an incoming invoice."
   - *(Drag and drop your Water Bottles PDF into the upload zone)*.
   - "Behind the scenes, the system converts this file into text and passes it through our AI Extraction Prompt using OpenAI/Gemini Vision to structure the unstructured data into JSON."

---

## 🧠 Step 3: Explainable AI & Results (2 mins)
1. **Review the Results Screen**:
   - *(The screen will show APPROVED)*
   - "As you can see, the AI didn't just extract the data; it ran it through two custom Python microservices: a Validation Engine and a Fraud Engine."
   - **Scroll to Validation Engine**:
     - "Because the AI extracted 'Water Bottles' for a total of $200,000, and our database had an exact match for that description and amount, the Validation Engine automatically passed it!" 
     - "If someone tried to bill us for 'Arc Reactor Parts' on this PO, the system would immediately flag a Line Item Mismatch and halt the payment."
   - **Scroll to Fraud Engine**:
     - "The Fraud Engine also checked the vendor status and duplicate history. Because Stark Industries is in good standing and this isn't a duplicate, the Fraud Score is low."
   - **Explainable AI Reason**:
     - "Finally, our secondary LLM decision engine looked at all the results and generated this human-readable explanation, confidently marking the invoice as APPROVED."

---

## 📊 Step 4: Analytics Dashboard (1 min)
1. **Click on 'Analytics Dashboard'**:
   - "All this data flows back into a central dashboard for the finance team."
   - "We can see our KPIs update in real-time, and we have a full audit log of recent invoice ingestions, proving the end-to-end automation works flawlessly."

---

## 🏁 Conclusion (30 secs)
"In conclusion, this architecture provides a scalable, secure, and highly intelligent solution for automated invoice processing. Thank you for your time, and I look forward to your feedback!"
