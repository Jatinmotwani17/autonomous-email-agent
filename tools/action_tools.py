from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "actions.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def process_refund(customer_id: str, amount: float) -> Dict[str, Any]:
    return {
        "refund_id": f"REF-{uuid.uuid4().hex[:8]}",
        "status": "SUCCESS",
        "amount": amount,
        "timestamp": _utc_now(),
        "customer_id": customer_id,
    }


def process_cancellation(customer_id: str) -> Dict[str, Any]:
    return {
        "cancellation_id": f"CAN-{uuid.uuid4().hex[:8]}",
        "status": "SUCCESS",
        "timestamp": _utc_now(),
        "customer_id": customer_id,
    }


def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    return {
        "email_id": f"EMAIL-{uuid.uuid4().hex[:8]}",
        "status": "SUCCESS",
        "sent_to": to,
        "subject": subject,
        "timestamp": _utc_now(),
    }


def send_password_reset_link(customer_email: str) -> Dict[str, Any]:
    return {
        "reset_token": f"RST-{uuid.uuid4().hex[:10]}",
        "status": "SUCCESS",
        "sent_to": customer_email,
        "timestamp": _utc_now(),
    }


def create_support_ticket(customer_id: str, issue: str, priority: str) -> Dict[str, Any]:
    return {
        "ticket_id": f"TCK-{uuid.uuid4().hex[:8]}",
        "status": "SUCCESS",
        "priority": priority,
        "issue": issue,
        "timestamp": _utc_now(),
        "customer_id": customer_id,
    }


def notify_human(message: str) -> Dict[str, Any]:
    return {
        "escalation_id": f"ESC-{uuid.uuid4().hex[:8]}",
        "status": "SUCCESS",
        "message": message,
        "timestamp": _utc_now(),
    }


def log_action(action_data: Dict[str, Any]) -> Dict[str, Any]:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOG_PATH.exists():
        existing = json.loads(LOG_PATH.read_text(encoding="utf-8") or "[]")
    else:
        existing = []

    action_id = f"ACT-{uuid.uuid4().hex[:8]}"
    log_entry = {
        "action_id": action_id,
        "logged_at": _utc_now(),
        "data": action_data,
    }
    existing.append(log_entry)

    LOG_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return {"logged_at": log_entry["logged_at"], "action_id": action_id}
