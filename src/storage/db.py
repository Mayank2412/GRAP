import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = "grievance_automation.db"

import os

def get_default_db_path():
    # If in sandbox 9p filesystem, use /tmp to prevent disk I/O locking errors
    if os.path.exists("/working_dir") and os.name != "nt":
        return "/tmp/grievance_automation.db"
    return "grievance_automation.db"

DB_PATH = get_default_db_path()

def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_requests (
            sr_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            customer_id TEXT,
            product_domain TEXT NOT NULL,
            sub_category TEXT NOT NULL,
            priority TEXT NOT NULL,
            is_regulatory BOOLEAN NOT NULL,
            tat_deadline_hours INTEGER NOT NULL,
            intake_json TEXT NOT NULL,
            evidence_docket TEXT,
            decision_json TEXT,
            qc_json TEXT,
            final_response TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sr_id TEXT NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

class SRRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def register_sr(self, intake_data: Dict[str, Any]) -> str:
        sr_id = intake_data["sr_id"]
        now = datetime.utcnow().isoformat()
        cust_id = intake_data.get("customer_identifiers", {}).get("customer_id")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO service_requests (
                sr_id, status, customer_id, product_domain, sub_category,
                priority, is_regulatory, tat_deadline_hours, intake_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sr_id,
            "REGISTERED",
            cust_id,
            intake_data["product_domain"],
            intake_data["sub_category"],
            intake_data["priority"],
            intake_data.get("regulatory_details", {}).get("is_regulatory_escalation", False),
            intake_data.get("regulatory_details", {}).get("tat_deadline_hours", 720),
            json.dumps(intake_data),
            now,
            now
        ))
        
        # Log audit entry
        cursor.execute("""
            INSERT INTO audit_logs (sr_id, action, actor, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (sr_id, "SR_REGISTERED", "SRRegistrationAgent (RPA)", f"SR registered via intake channel with priority {intake_data['priority']}", now))
        
        conn.commit()
        conn.close()
        return sr_id

    def update_evidence(self, sr_id: str, evidence: Dict[str, Any]):
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE service_requests
            SET status = 'EVIDENCE_COLLECTED', evidence_docket = ?, updated_at = ?
            WHERE sr_id = ?
        """, (json.dumps(evidence), now, sr_id))
        
        cursor.execute("""
            INSERT INTO audit_logs (sr_id, action, actor, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (sr_id, "EVIDENCE_COLLECTED", "CaseHandlingOrchestrator", f"Dispatched queries to {list(evidence.keys())}", now))
        
        conn.commit()
        conn.close()

    def get_sr(self, sr_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM service_requests WHERE sr_id = ?", (sr_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "sr_id": row[0],
            "status": row[1],
            "customer_id": row[2],
            "product_domain": row[3],
            "sub_category": row[4],
            "priority": row[5],
            "is_regulatory": bool(row[6]),
            "tat_deadline_hours": row[7],
            "intake_json": json.loads(row[8]),
            "evidence_docket": json.loads(row[9]) if row[9] else None,
            "decision_json": json.loads(row[10]) if row[10] else None,
            "qc_json": json.loads(row[11]) if row[11] else None,
            "final_response": row[12],
            "created_at": row[13],
            "updated_at": row[14]
        }
