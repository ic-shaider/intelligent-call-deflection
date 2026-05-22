"""Deflection Strategy Agent — Determines optimal deflection path."""
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.database import CallReason, DeflectionChannel

STRATEGY_MAP = {
    CallReason.PAYMENT_DUE: [DeflectionChannel.SMS_PAYMENT_LINK, DeflectionChannel.PORTAL_REDIRECT],
    CallReason.FAILED_PAYMENT: [DeflectionChannel.SMS_PAYMENT_LINK, DeflectionChannel.CHATBOT],
    CallReason.BALANCE_INQUIRY: [DeflectionChannel.SMS_PAYMENT_LINK, DeflectionChannel.PORTAL_REDIRECT],
    CallReason.PAYMENT_CONFIRMATION: [DeflectionChannel.EMAIL_RESOLUTION],
    CallReason.AUTOPAY_ISSUE: [DeflectionChannel.CHATBOT, DeflectionChannel.CALLBACK_SCHEDULE],
    CallReason.ACCOUNT_CHANGE: [DeflectionChannel.PORTAL_REDIRECT, DeflectionChannel.CHATBOT],
    CallReason.OUTAGE_INQUIRY: [DeflectionChannel.CHATBOT],
    CallReason.GENERAL: [DeflectionChannel.CHATBOT, DeflectionChannel.CALLBACK_SCHEDULE],
}

MESSAGES = {
    DeflectionChannel.SMS_PAYMENT_LINK: "We can send you a secure payment link via text right now — takes 30 seconds to pay. Would you like that?",
    DeflectionChannel.CHATBOT: "Our AI assistant can help resolve this immediately via chat. I can transfer you there now.",
    DeflectionChannel.PORTAL_REDIRECT: "You can view and manage this on your online account. I can text you the link.",
    DeflectionChannel.CALLBACK_SCHEDULE: "I can schedule a callback from a specialist at a time that works for you.",
    DeflectionChannel.EMAIL_RESOLUTION: "We'll send you a confirmation email with all the details within 5 minutes.",
}


class DeflectionStrategyAgent:
    def __init__(self):
        self.name = "DeflectionStrategyAgent"
        self.status = "healthy"
        self.last_run: Optional[datetime] = None
        self.records_processed = 0

    def determine_strategy(self, reason: str, confidence: float, preferred_channel: str = None) -> Dict[str, Any]:
        call_reason = CallReason(reason)
        channels = STRATEGY_MAP.get(call_reason, [DeflectionChannel.CHATBOT])

        # Prefer account's preferred channel if available
        if preferred_channel:
            for ch in channels:
                if preferred_channel.lower() in ch.value:
                    channels = [ch] + [c for c in channels if c != ch]
                    break

        primary = channels[0] if channels else DeflectionChannel.NONE
        should_deflect = confidence >= 0.5

        self.records_processed += 1
        self.last_run = datetime.utcnow()

        return {
            "should_deflect": should_deflect,
            "primary_channel": primary.value,
            "fallback_channel": channels[1].value if len(channels) > 1 else None,
            "deflection_script": MESSAGES.get(primary, ""),
            "estimated_cost_saving": 5.50 if should_deflect else 0.0,
        }
