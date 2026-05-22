"""API routes for Intelligent Call Deflection."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import get_db, InboundCall, DeflectionMetrics, DeflectionOutcome
from app.agents.orchestrator import DeflectionOrchestrator

router = APIRouter(prefix="/api/v1")
orchestrator = DeflectionOrchestrator()


class CallRequest(BaseModel):
    caller_phone: str
    account_id: str


@router.post("/calls/process")
def process_call(req: CallRequest, db: Session = Depends(get_db)):
    return orchestrator.process_call(db, req.caller_phone, req.account_id)


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total = db.query(InboundCall).count()
    deflected = db.query(InboundCall).filter(InboundCall.outcome == DeflectionOutcome.DEFLECTED).count()
    completed = db.query(InboundCall).filter(InboundCall.outcome == DeflectionOutcome.COMPLETED_DIGITAL).count()
    cost_saved = db.query(func.sum(InboundCall.cost_saved)).scalar() or 0
    avg_conf = db.query(func.avg(InboundCall.prediction_confidence)).scalar() or 0
    return {
        "total_calls": total, "deflected": deflected, "completed_digital": completed,
        "deflection_rate": round(deflected / max(total, 1) * 100, 1),
        "total_cost_saved": round(cost_saved, 2), "avg_confidence": round(avg_conf, 3),
    }


@router.get("/calls")
def list_calls(limit: int = 50, db: Session = Depends(get_db)):
    calls = db.query(InboundCall).order_by(InboundCall.created_at.desc()).limit(limit).all()
    return {"calls": [{"call_id": c.call_id, "account": c.account_id, "biller": c.biller_name,
                       "reason": c.predicted_reason.value if c.predicted_reason else None,
                       "confidence": c.prediction_confidence, "channel": c.deflection_channel.value if c.deflection_channel else None,
                       "outcome": c.outcome.value if c.outcome else None, "cost_saved": c.cost_saved,
                       "time": c.created_at.isoformat() if c.created_at else None} for c in calls]}


@router.get("/agents/status")
def agent_status():
    return orchestrator.get_status()
