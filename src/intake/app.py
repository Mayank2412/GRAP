import sys
sys.path.insert(0, '/working_dir/c_091f4c4879d0f9ea/grievance_automation/src/intake')

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from models import GrievanceCaseOutput
from parser import EmailGrievanceParser

app = FastAPI(
    title="Grievance Redressal Automation - Email Intake Service",
    description="Gen-AI Supported RPA Ingestion Service for BFSI Regulatory Grievances",
    version="1.0.0"
)

parser = EmailGrievanceParser()

class EmailInputPayload(BaseModel):
    sender_name: Optional[str] = Field(None, example="Rajiv Malhotra")
    sender_email: str = Field(..., example="rajiv.malhotra82@gmail.com")
    subject: str = Field(..., example="URGENT: Unauthorized transaction on Credit Card - Escalation to RBI Ombudsman")
    body: str = Field(..., example="Dear Nodal Officer, unauthorized charge of Rs. 48,500 on card ending 4491...")
    received_at: Optional[str] = None

@app.get("/health")
def health_check():
    return {"status": "ACTIVE", "system": "Grievance Redressal Automation Engine"}

@app.post("/api/v1/ingest/email", response_model=GrievanceCaseOutput)
def ingest_email(payload: EmailInputPayload):
    try:
        return parser.process_email_payload(payload.dict())
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
