"""Call Deflection Orchestrator."""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.agents.intent_predictor import CallIntentPredictor
from app.agents.deflection_strategy import DeflectionStrategyAgent
from app.agents.context_enrichment import ContextEnrichmentAgent
from app.models.database import InboundCall, DeflectionOutcome
import uuid


class DeflectionOrchestrator:
    def __init__(self):
        self.intent_predictor = CallIntentPredictor()
        self.strategy_agent = DeflectionStrategyAgent()
        self.context_agent = ContextEnrichmentAgent()
        self.calls_processed = 0
        self.last_run: Optional[datetime] = None

    def process_call(self, db: Session, caller_phone: str, account_id: str) -> Dict[str, Any]:
        call_id = f"CALL-{uuid.uuid4().hex[:8].upper()}"

        # Step 1: Predict intent
        prediction = self.intent_predictor.predict(db, account_id)

        # Step 2: Determine strategy
        strategy = self.strategy_agent.determine_strategy(
            prediction["reason"], prediction["confidence"]
        )

        # Step 3: Enrich context
        context = self.context_agent.enrich(db, account_id)

        # Step 4: Record call
        outcome = DeflectionOutcome.DEFLECTED if strategy["should_deflect"] else DeflectionOutcome.DECLINED_STAYED
        call = InboundCall(
            call_id=call_id, caller_phone=caller_phone, account_id=account_id,
            biller_name=context.get("biller", "Unknown"),
            predicted_reason=prediction["reason"],
            prediction_confidence=prediction["confidence"],
            deflection_channel=strategy["primary_channel"],
            outcome=outcome,
            cost_saved=strategy["estimated_cost_saving"],
            context_data=context,
        )
        db.add(call)
        db.commit()

        self.calls_processed += 1
        self.last_run = datetime.utcnow()

        return {
            "call_id": call_id, "prediction": prediction,
            "strategy": strategy, "context": context, "outcome": outcome.value,
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "orchestrator": {"calls_processed": self.calls_processed, "last_run": self.last_run.isoformat() if self.last_run else None},
            "agents": [
                {"name": self.intent_predictor.name, "status": self.intent_predictor.status, "records_processed": self.intent_predictor.records_processed},
                {"name": self.strategy_agent.name, "status": self.strategy_agent.status, "records_processed": self.strategy_agent.records_processed},
                {"name": self.context_agent.name, "status": self.context_agent.status, "records_processed": self.context_agent.records_processed},
            ]
        }
