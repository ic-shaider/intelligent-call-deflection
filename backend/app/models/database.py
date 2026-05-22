"""Database models for Intelligent Call Deflection."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, Text, JSON, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
DATABASE_URL = "sqlite:///./call_deflection.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CallReason(str, PyEnum):
    PAYMENT_DUE = "payment_due"
    FAILED_PAYMENT = "failed_payment"
    BALANCE_INQUIRY = "balance_inquiry"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    AUTOPAY_ISSUE = "autopay_issue"
    ACCOUNT_CHANGE = "account_change"
    OUTAGE_INQUIRY = "outage_inquiry"
    GENERAL = "general"


class DeflectionChannel(str, PyEnum):
    SMS_PAYMENT_LINK = "sms_payment_link"
    CHATBOT = "chatbot"
    PORTAL_REDIRECT = "portal_redirect"
    CALLBACK_SCHEDULE = "callback_schedule"
    EMAIL_RESOLUTION = "email_resolution"
    NONE = "none"


class DeflectionOutcome(str, PyEnum):
    DEFLECTED = "deflected"
    ACCEPTED_DIGITAL = "accepted_digital"
    DECLINED_STAYED = "declined_stayed"
    COMPLETED_DIGITAL = "completed_digital"
    RETURNED_TO_CALL = "returned_to_call"


class InboundCall(Base):
    __tablename__ = "inbound_calls"
    id = Column(Integer, primary_key=True)
    call_id = Column(String(50), unique=True)
    caller_phone = Column(String(20))
    account_id = Column(String(50))
    biller_name = Column(String(200))
    predicted_reason = Column(Enum(CallReason))
    prediction_confidence = Column(Float)
    deflection_channel = Column(Enum(DeflectionChannel))
    outcome = Column(Enum(DeflectionOutcome))
    cost_saved = Column(Float, default=0.0)
    context_data = Column(JSON)
    call_duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountContext(Base):
    __tablename__ = "account_contexts"
    id = Column(Integer, primary_key=True)
    account_id = Column(String(50), unique=True)
    customer_name = Column(String(200))
    biller_name = Column(String(200))
    balance = Column(Float, default=0.0)
    next_due_date = Column(DateTime)
    last_payment_date = Column(DateTime)
    last_payment_amount = Column(Float)
    autopay_enrolled = Column(Boolean, default=False)
    has_failed_payment = Column(Boolean, default=False)
    notification_sent_recently = Column(Boolean, default=False)
    preferred_channel = Column(String(50))


class DeflectionMetrics(Base):
    __tablename__ = "deflection_metrics"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    total_calls = Column(Integer, default=0)
    deflection_attempts = Column(Integer, default=0)
    successful_deflections = Column(Integer, default=0)
    cost_saved = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    top_reason = Column(String(50))
    top_channel = Column(String(50))


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
