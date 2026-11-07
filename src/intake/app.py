import sys
from pathlib import Path

# Dynamic multi-platform path setup
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
for p in [str(ROOT_DIR), str(SRC_DIR), str(SRC_DIR / "intake")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional

try:
    from src.intake.models import GrievanceCaseOutput, to_dict
    from src.intake.parser import EmailGrievanceParser
except (ImportError, ValueError):
    from models import GrievanceCaseOutput, to_dict
    from parser import EmailGrievanceParser

app = FastAPI(
    title="Grievance Redressal Automation - Email Intake Service",
    description="Gen-AI Supported RPA Ingestion Service for BFSI Regulatory Grievances",
    version="1.0.0"
)

parser = EmailGrievanceParser()

class EmailInputPayload(BaseModel):
    sender_name: Optional[str] = Field(None, description="Sender name")
    sender_email: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    received_at: Optional[str] = None

@app.get("/health")
def health_check():
    return {"status": "ACTIVE", "system": "Grievance Redressal Automation Engine"}

@app.post("/api/v1/ingest/email", response_model=GrievanceCaseOutput)
def ingest_email(payload: EmailInputPayload):
    try:
        return parser.process_email_payload(to_dict(payload))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ingest/raw-eml", response_model=GrievanceCaseOutput)
def ingest_raw_eml(raw_content: str = Body(..., media_type="text/plain")):
    try:
        return parser.parse_raw_email(raw_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
