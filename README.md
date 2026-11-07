# Grievance Redressal Automation Program (GRAP)

An enterprise-grade hybrid Agentic AI & Gen-AI supported RPA architecture designed for Tier-1 BFSI organizations to automate end-to-end Regulatory Grievance Handling (such as Reserve Bank of India Ombudsman escalations).

---

## Architecture Overview

```text
Inbound Email / Regulatory Portal
               │
               ▼
┌──────────────────────────────────────────────┐
│  1. INTELLIGENT TRIAGING SYSTEM (RPA Tier)   │
│  - Email & RFC 822 MIME Ingestion            │
│  - PII Masking & Schema Validation           │
│  - SR Registration & SLA Priority Assignment │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  2. CASE HANDLING ORCHESTRATOR               │
│  - State Machine Management (SQLite/CRMNext) │
│  - Concurrent Queries to Core Banking Adapters│
└──────────────────────┬───────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  CRMNext    │ │   Finacle   │ │  CTL Prime  │
│Customer 360 │ │ Core Ledger │ │ Cards / CMS │
└─────────────┘ └─────────────┘ └─────────────┘
       ▲               ▲               ▲
       └───────────────┼───────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌─────────────┐                 ┌─────────────┐
│   FinOne    │                 │  Data Lake  │
│LMS / Lending│                 │ Telemetry   │
└─────────────┘                 └─────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  3. INVESTIGATION DOCKET COMPILER            │
│  - Cross-system Timeline Reconstruction      │
│  - Anomaly Detection (Geo-Velocity, 3DS)     │
│  - Statutory Policy Violation Flagging       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  4. INTELLIGENT DECISIONING SYSTEM (Agents)  │
│  - Cards Decision Agent (RBI Zero Liability) │
│  - Assets Decision Agent (Foreclosure Rules) │
│  - Monetary & Non-Monetary Relief Directives │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  5. REAL-TIME QC SYSTEM (Guardrail Gate)     │
│  - Responsible AI Agent (PII & Tone Audit)   │
│  - Response Validation Agent (Ledger Check)  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  6. OUTBOUND RESPONSE SYSTEM                 │
│  - Formal Customer & Ombudsman Notice        │
│  - Denial of Service / Handover Engine       │
│  - Immutable Audit Log & SR Closure          │
└──────────────────────────────────────────────┘
```

---

## Directory Structure

```text
grievance_automation/
├── README.md               # Architecture documentation
├── requirements.txt        # Runtime dependencies
├── .gitignore              # Standard git exclusions
├── main_pipeline.py        # Master E2E runner (Stages 1 through 6)
├── test_intake.py          # Stage 1 standalone test
├── test_orchestrator.py    # Stages 1 to 3 standalone test
└── src/
    ├── intake/
    │   ├── models.py       # Pydantic schemas, domains, and SLA models
    │   ├── parser.py       # Gen-AI RPA parser for email extraction
    │   └── app.py          # FastAPI HTTP ingestion server
    ├── storage/
    │   └── db.py           # SQLite repository tracking SR lifecycle
    ├── adapters/
    │   ├── crmnext.py      # Customer 360 profile & wealth tier
    │   ├── finacle.py      # Core banking accounts & ledgers
    │   ├── ctl_prime.py    # Card management & 3DS authorization logs
    │   ├── finone.py       # Lending terms & foreclosure penalty checks
    │   └── data_lake.py    # Telemetry, geolocation & anomaly scoring
    ├── orchestration/
    │   └── orchestrator.py # Case Handling Orchestrator & Evidence compiler
    ├── decisioning/
    │   ├── domain_agents.py# Cards, Assets, Accounts, and Liabilities agents
    │   └── engine.py       # Domain router and decision engine
    ├── qc/
    │   ├── responsible_ai.py # PII safety, tone, and compliance auditor
    │   └── validator.py    # Factual verification against core ledgers
    └── outbound/
        ├── templates.py    # Official bank and Ombudsman resolution notices
        └── dispatcher.py   # Final dispatch and state transition handler
```

---

## Quickstart

### 1. Run Complete Pipeline (All 6 Stages)
```bash
python main_pipeline.py
```

### 2. Run Intake Tests
```bash
python test_intake.py
```

### 3. Run Ingestion API Server
```bash
python src/intake/app.py
```
Visit `http://127.0.0.1:8000/docs` for the interactive Swagger API documentation.
