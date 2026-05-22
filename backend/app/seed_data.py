"""Seed data for Call Deflection."""
import random
from datetime import datetime, timedelta
from app.models.database import (init_db, SessionLocal, AccountContext, InboundCall, DeflectionMetrics,
                                  CallReason, DeflectionChannel, DeflectionOutcome)

BILLERS = ["CDE Lightband", "Soquel Creek Water", "City of Wylie TX", "Texas Farm Bureau",
           "Safety Insurance", "FCCI Insurance", "Flagstaff AZ", "JCSA Water"]
NAMES = ["James Smith", "Maria Garcia", "Robert Johnson", "Linda Williams", "Michael Brown",
         "Susan Davis", "David Wilson", "Jessica Martinez", "Thomas Anderson", "Karen Taylor"]


def seed():
    init_db()
    db = SessionLocal()
    db.query(InboundCall).delete()
    db.query(AccountContext).delete()
    db.query(DeflectionMetrics).delete()
    db.commit()

    # Create 80 accounts
    for i in range(80):
        biller = random.choice(BILLERS)
        ctx = AccountContext(
            account_id=f"ACCT-{10000+i}", customer_name=random.choice(NAMES),
            biller_name=biller, balance=round(random.uniform(30, 500), 2),
            next_due_date=datetime.utcnow() + timedelta(days=random.randint(-5, 20)),
            last_payment_date=datetime.utcnow() - timedelta(days=random.randint(10, 60)),
            last_payment_amount=round(random.uniform(50, 300), 2),
            autopay_enrolled=random.random() < 0.4,
            has_failed_payment=random.random() < 0.25,
            notification_sent_recently=random.random() < 0.4,
            preferred_channel=random.choice(["sms", "email", "portal"]),
        )
        db.add(ctx)

    # Historical calls
    for i in range(200):
        reason = random.choice(list(CallReason))
        channel = random.choice(list(DeflectionChannel))
        outcome = random.choice(list(DeflectionOutcome))
        db.add(InboundCall(
            call_id=f"CALL-{i:06d}", caller_phone=f"+1555{random.randint(1000000,9999999)}",
            account_id=f"ACCT-{random.randint(10000,10079)}", biller_name=random.choice(BILLERS),
            predicted_reason=reason, prediction_confidence=round(random.uniform(0.4, 0.95), 3),
            deflection_channel=channel, outcome=outcome,
            cost_saved=5.50 if outcome in (DeflectionOutcome.DEFLECTED, DeflectionOutcome.COMPLETED_DIGITAL) else 0,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
        ))

    # Daily metrics
    for d in range(30):
        total = random.randint(50, 150)
        deflected = int(total * random.uniform(0.35, 0.65))
        db.add(DeflectionMetrics(
            date=datetime.utcnow() - timedelta(days=d), total_calls=total,
            deflection_attempts=total, successful_deflections=deflected,
            cost_saved=round(deflected * 5.50, 2), avg_confidence=round(random.uniform(0.6, 0.85), 3),
            top_reason=random.choice(list(CallReason)).value, top_channel=random.choice(list(DeflectionChannel)).value,
        ))

    db.commit()
    db.close()
    print("✓ Seeded 80 accounts, 200 calls, 30 days metrics")


if __name__ == "__main__":
    seed()
