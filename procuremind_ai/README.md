# ProcureMind AI - Invoice Validation & PO Matching System

ProcureMind AI is an enterprise-grade Procurement AI software designed to fully automate the processing, validation, and fraud-checking of incoming vendor invoices.

This project was built as the submission for the AI Engineer Round 3 Technical Assignment.

## Architecture & Features

We deviated from a basic no-code integration to build a highly robust, fully-fledged **Hybrid SaaS Application** using Python (Flask), a local SQLite database, and advanced API-driven LLM integrations (OpenAI / Gemini).

### Key Features
1. **Dynamic UI Dashboard**: A sleek, custom-built frontend (HTML/CSS/JS) for processing invoices, viewing analytics, and managing Master Data.
2. **AI-Powered OCR**: Extracts text from PDFs and Images, supporting multiple formats (PDF, JPG, PNG, Excel, CSV, TXT) and multiple providers (OpenAI GPT-4o, Google Gemini Flash).
3. **Advanced Line-Item 3-Way Matching**: The Validation Engine compares individual line items on the invoice (quantities and prices) against the Purchase Order line items, instead of just checking the header total.
4. **Fraud & Duplicate Detection Engine**: Automatically flags duplicate invoices, blacklisted/inactive vendors, and mathematically anomalous billing (e.g. Net + Tax != Gross).
5. **Auto-Vendor Creation**: If an invoice arrives from an unknown vendor, the system automatically creates the vendor profile but flags it as `HIGH` risk for procurement review.

## Setup Instructions

### Prerequisites
- Python 3.9+ installed
- Windows OS (or modify the batch file for Mac/Linux)

### Installation
1. Clone this repository to your local machine.
2. Open a terminal in the `/microservices/unified_engine` directory.
3. Install required packages:
   ```bash
   pip install flask openai google-generativeai PyPDF2
   ```
4. Run the server using the provided batch script (from the root of the repo):
   ```bash
   start_services.bat
   ```
   *Alternatively, just run `python app.py` inside the unified_engine folder.*
5. Open your browser and navigate to: `http://127.0.0.1:8000`

### Usage
1. Go to the **AI Settings** tab and enter your OpenAI or Gemini API Key.
2. Go to the **Master Data** tab to review or create a Vendor and a Purchase Order (with line items).
3. Go to the **Invoice Processing** tab and upload a test Invoice PDF.
4. Review the AI Intelligence Layer's Explainable AI results!

## Repository Structure
- `/microservices/unified_engine/`: The core application directory.
  - `app.py`: The main Flask routing engine.
  - `/database/db.py`: SQLite schema and ORM logic.
  - `/services/ai_service.py`: LLM Prompts and Extraction Logic.
  - `/services/validation_service.py`: 3-way matching math algorithms.
  - `/services/fraud_service.py`: Risk and duplicate analysis.
  - `/services/decision_engine.py`: Final decision matrix logic.
  - `/templates/`: The frontend HTML UI.
  - `/static/`: CSS and Images (Logo).
- `DATABASE_SCHEMA.md`: Details of the SQLite tables.
- `AI_PROMPTS.md`: The exact system prompts used in the backend.
- `DEMO_VIDEO_SCRIPT.md`: Outline used for the video presentation.
