"""Call Intent Predictor — Predicts why caller is calling based on account state."""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import AccountContext, CallReason


class CallIntentPredictor:
    def __init__(self):
        self.name = "CallIntentPredictor"
        self.status = "healthy"
        self.last_run: Optional[datetime] = None
        self.records_processed = 0

    def predict(self, db: Session, account_id: str) -> Dict[str, Any]:
        ctx = db.query(AccountContext).filter(AccountContext.account_id == account_id).first()
        if not ctx:
            return {"reason": CallReason.GENERAL.value, "confidence": 0.3, "signals": []}

        signals = []
        scores = {r: 0.0 for r in CallReason}

        # Failed payment signal
        if ctx.has_failed_payment:
            scores[CallReason.FAILED_PAYMENT] += 0.4
            signals.append("Recent failed payment detected")

        # Due date approaching
        if ctx.next_due_date:
            days_to_due = (ctx.next_due_date - datetime.utcnow()).days
            if 0 <= days_to_due <= 3:
                scores[CallReason.PAYMENT_DUE] += 0.35
                signals.append(f"Payment due in {days_to_due} days")
            elif days_to_due < 0:
                scores[CallReason.PAYMENT_DUE] += 0.45
                signals.append(f"Payment {abs(days_to_due)} days overdue")

        # Recent notification
        if ctx.notification_sent_recently:
            scores[CallReason.PAYMENT_CONFIRMATION] += 0.2
            signals.append("Notification sent recently")

        # Balance check
        if ctx.balance > 0 and not ctx.has_failed_payment:
            scores[CallReason.BALANCE_INQUIRY] += 0.15

        # AutoPay issues
        if ctx.autopay_enrolled and ctx.has_failed_payment:
            scores[CallReason.AUTOPAY_ISSUE] += 0.35
            signals.append("AutoPay enrolled but payment failed")

        best_reason = max(scores, key=scores.get)
        confidence = min(max(scores[best_reason] + 0.3, 0.3), 0.95)

        self.records_processed += 1
        self.last_run = datetime.utcnow()

        return {
            "reason": best_reason.value,
            "confidence": round(confidence, 3),
            "signals": signals,
            "account": {"name": ctx.customer_name, "biller": ctx.biller_name, "balance": ctx.balance},
        }
