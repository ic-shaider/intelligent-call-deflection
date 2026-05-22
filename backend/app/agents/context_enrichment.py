"""Context Enrichment Agent — Pre-fetches account context for digital channels."""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import AccountContext


class ContextEnrichmentAgent:
    def __init__(self):
        self.name = "ContextEnrichmentAgent"
        self.status = "healthy"
        self.last_run: Optional[datetime] = None
        self.records_processed = 0

    def enrich(self, db: Session, account_id: str) -> Dict[str, Any]:
        ctx = db.query(AccountContext).filter(AccountContext.account_id == account_id).first()
        if not ctx:
            return {"error": "Account not found"}

        context_package = {
            "account_id": ctx.account_id,
            "customer_name": ctx.customer_name,
            "biller": ctx.biller_name,
            "balance": ctx.balance,
            "next_due": ctx.next_due_date.isoformat() if ctx.next_due_date else None,
            "last_payment": {"date": ctx.last_payment_date.isoformat() if ctx.last_payment_date else None, "amount": ctx.last_payment_amount},
            "autopay": ctx.autopay_enrolled,
            "has_failed_payment": ctx.has_failed_payment,
            "payment_link": f"https://pay.invoicecloud.net/{ctx.account_id}",
            "portal_link": f"https://portal.invoicecloud.net/{ctx.biller_name.lower().replace(' ', '-')}/{ctx.account_id}",
        }

        self.records_processed += 1
        self.last_run = datetime.utcnow()
        return context_package
