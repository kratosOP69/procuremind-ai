# ProcureMind AI - Demo Script

## Goal
Demonstrate the end-to-end capabilities of the ProcureMind AI platform to key stakeholders.

## Pre-requisites
- Ensure n8n workflows are active.
- Ensure Airtable `Vendors` and `Purchase Orders` have mock data (e.g., PO-500 for TechCorp for $1,100).
- Open the Slack #procurement-approvals channel.
- Open the Airtable Invoices view.

## Scenario 1: The "Perfect" Invoice (Auto-Approval)
**Action:**
1. Send an email to the procurement inbox with `perfect_invoice.pdf` attached. (Matches PO-500 exactly).
2. Show the n8n execution UI tracing the email.
3. Switch to Airtable.
**Talking Points:**
- "The AI extracts the PDF, matches it to PO-500, validates the math, and runs a fraud check."
- "Because everything matches and risk is low, it bypasses human review and goes straight to 'Approved' status."

## Scenario 2: Minor Discrepancy (Tolerance / Human Review)
**Action:**
1. Send an email with `shipping_fee_invoice.pdf`. (Gross amount is $1,115 - slightly higher due to shipping).
2. Wait 30 seconds.
3. Open Slack.
**Talking Points:**
- "Here, the vendor added an unexpected shipping fee."
- "The Validation Engine detected a variance of $15. Since it's under the 2% tolerance, it flags it as a 'Warning'."
- "Instead of rejecting it, it routes to Slack for human review."
4. Click the link in Slack to open Airtable, and manually change Status to "Approved". Show the Audit Log capturing this override.

## Scenario 3: High Fraud Risk (Rejection)
**Action:**
1. Send an email with `duplicate_invoice.pdf` (same invoice number as Scenario 1).
2. Check Slack/Airtable.
**Talking Points:**
- "The Fraud Engine instantly caught the duplicate invoice number for this vendor. It scored a 70 (HIGH risk)."
- "The decision engine automatically halts payment and flags it for forensic review."
