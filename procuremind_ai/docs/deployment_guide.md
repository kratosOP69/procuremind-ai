# ProcureMind AI - Deployment Guide

## 1. Prerequisites
- Docker & Docker Compose
- Node.js & npm (for n8n local testing)
- Python 3.11+
- Access to Airtable
- Slack Workspace Administrator access

## 2. Infrastructure Setup (AWS / Kubernetes)

### Microservices
The Validation and Fraud engines are designed as lightweight FastAPI applications.
1. Build the Docker images:
   ```bash
   docker build -t procuremind/validation-engine ./microservices/validation_engine
   docker build -t procuremind/fraud-engine ./microservices/fraud_engine
   ```
2. Deploy to AWS ECS / Fargate or a Kubernetes cluster.
3. Expose them via an internal application load balancer. Ensure they are not publicly accessible on the internet.

### n8n Orchestration Layer
1. Deploy n8n via Docker or use n8n Cloud.
2. In the n8n UI, navigate to **Credentials**.
3. Create the following credentials:
   - **Airtable API**: Add your PAT.
   - **OpenAI API**: Add your API Key.
   - **AWS Textract**: Add your IAM keys (ensure least-privilege IAM policy).
   - **Slack API**: Add the bot token.
4. Import the 3 workflows from `/n8n_workflows`.
5. Update the HTTP Request nodes in Workflow 3 to point to your deployed microservice URLs.

## 3. Database Setup (Airtable)
1. Import `airtable_schema.json` to create the exact base structure.
2. Ensure you have some mock data in the `Vendors` and `Purchase Orders` tables before running the demo.

## 4. Environment Configuration
Populate the `.env` file and mount it to your Docker containers.

## 5. Maintenance and Logging
- n8n executions should be monitored via the n8n executions UI. Failed executions should trigger a Slack webhook to DevOps.
- Microservices emit standard JSON logs on stdout. Forward these to AWS CloudWatch or Datadog using FluentBit.
