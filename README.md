# Intelligent Call Deflection Agent

> **Non-Hackathon Bucket — PoC Idea #2**
>
> Extends the Vista Hackathon "Call Deflector" PoC into a production-ready system
> that deflects inbound calls to digital self-service channels using AI intent
> detection and proactive context-fetching.

## What This Is

A **multi-agent call deflection system** that intercepts inbound IVR calls and routes
callers to faster digital resolution paths:

1. **Call Intent Predictor Agent** — Predicts why the caller is calling based on account state (upcoming due date, failed payment, recent notification)
2. **Deflection Strategy Agent** — Determines optimal deflection path (SMS link, chatbot, portal, callback scheduling)
3. **Context Enrichment Agent** — Pre-fetches account context so digital channels have full information ready
4. **Deflection Dashboard** — Tracks deflection rates, cost savings, caller satisfaction

## Architecture

```
Inbound Call → IVR Intercept → Intent Predictor → Deflection Strategy → Digital Channel
                                      ↓                    ↓
                              Context Enrichment    SMS/Chat/Portal
```

## Quick Start

```bash
cd backend && pip install -r requirements.txt && python -m app.seed_data && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

## IC Context

- **ServiceIQ**: 6 agents, 20+ tools — our deflection targets
- **Vista Hackathon**: "Big Billy Style" Call Deflector proved concept with Glia + MCP
- **BillerIVRTechAPI**: Current IVR — intercept point for deflection
- **Cost**: Average call costs $5-8; digital resolution costs $0.50-1.50

## License

Internal InvoiceCloud use only.
