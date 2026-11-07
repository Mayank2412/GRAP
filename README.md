# Grievance Redressal Automation Program

An enterprise-grade hybrid architecture for BFSI Regulatory Grievance Handling, combining Gen-AI supported RPA for deterministic ingestion and data retrieval with Autonomous Agents for dispute orchestration, root-cause augmentation, decisioning, and real-time quality control.

## Project Structure
```
grievance_automation/
├── README.md
├── requirements.txt
├── test_intake.py
└── src/
    └── intake/
        ├── __init__.py
        ├── models.py       # Pydantic data models & schema validation
        ├── parser.py       # Gen-AI RPA Email & RFC 822 parser
        └── app.py          # FastAPI ingestion service
```

## Getting Started

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Intake Tests
```bash
python test_intake.py
```

### 3. Start Ingestion Service
```bash
python src/intake/app.py
```
Service runs at `http://127.0.0.1:8000`. Interactive Swagger documentation available at `http://127.0.0.1:8000/docs`.

## Git Initialization
```bash
git init
git add .
git commit -m "feat: initialize BFSI regulatory grievance intake engine"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```
