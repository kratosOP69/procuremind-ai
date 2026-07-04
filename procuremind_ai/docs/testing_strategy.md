# ProcureMind AI - Testing Strategy

## Overview
A robust testing strategy ensures high confidence when handling multi-million dollar invoices. We employ the testing pyramid approach.

## 1. Unit Tests
- **Scope**: Microservices (Validation Engine & Fraud Engine).
- **Framework**: `pytest`
- **Execution**: Run locally before commit, and automatically in CI/CD (GitHub Actions / GitLab CI).
- **Commands**:
  ```bash
  cd microservices/validation_engine
  pytest tests/
  ```
- **Coverage**: Minimum 90% required.

## 2. Integration Tests
- **Scope**: n8n Webhook -> Microservices -> Airtable
- **Execution**: Automated via Postman Collections / Newman in CI/CD against a staging environment.
- **Scenarios**:
  - Valid 3-way match -> Expect auto-approval.
  - Math error on invoice -> Expect Slack review routing.
  - Duplicate invoice number -> Expect high fraud score and rejection.

## 3. End-to-End (E2E) Testing
- **Scope**: Email drop -> n8n -> Extraction -> Validation -> Slack -> Airtable Approval
- **Execution**: Manual testing or RPA tools (like UiPath) to simulate vendor emails.
- **Test Data**: Use the standardized test PDF suite (containing 50 varied invoice layouts, scanned docs, and multi-page invoices).

## 4. Performance & Load Testing
- Simulate month-end peaks (e.g., 500 invoices per hour) using `locust`.
- Ensure n8n queue workers can scale horizontally to handle the Textract/LLM bottlenecks.
