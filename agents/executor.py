from __future__ import annotations

from typing import Any, Dict, List

from tools import action_tools


ACTION_HANDLERS = {
    "process_refund": "process_refund",
    "process_cancellation": "process_cancellation",
    "send_confirmation_email": "send_email",
    "send_acknowledgement_email": "send_email",
    "send_denial_email": "send_email",
    "send_email_no_active_sub": "send_email",
    "send_password_reset_link": "send_password_reset_link",
    "create_support_ticket": "create_support_ticket",
    "assign_priority": "create_support_ticket",
    "log_action": "log_action",
    "notify_human": "notify_human",
    "offer_support": "create_support_ticket",
    "log_feature_request": "log_action",
    "add_to_backlog": "log_action",
    "process_refund_if_applicable": "process_refund",
}


def _safe_float(value: Any, default: float = 29.99) -> float:
    try:
        return float(value)
    except Exception:
        return default


def execute_actions(action_plan: Dict[str, Any], email_context: Dict[str, Any]) -> Dict[str, Any]:
    actions = action_plan.get("actions", [])
    email_id = email_context.get("id") or email_context.get("email_id")
    customer_email = email_context.get("from") or email_context.get("customer_email")
    customer_id = email_context.get("customer_id") or (customer_email or "customer-unknown")
    subject = email_context.get("subject", "")
    body = email_context.get("body", "")

    actions_executed: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for action in actions:
        handler_name = ACTION_HANDLERS.get(action)
        if not handler_name or not hasattr(action_tools, handler_name):
            errors.append({"action": action, "error": "Unknown action"})
            actions_executed.append({"action": action, "status": "FAILED", "result": {"error": "Unknown action"}})
            continue

        try:
            if handler_name == "process_refund":
                result = action_tools.process_refund(customer_id, _safe_float(email_context.get("amount")))
            elif handler_name == "process_cancellation":
                result = action_tools.process_cancellation(customer_id)
            elif handler_name == "send_email":
                result = action_tools.send_email(
                    to=customer_email or "unknown@example.com",
                    subject=subject or "Support Update",
                    body=body or "We have received your request.",
                )
            elif handler_name == "send_password_reset_link":
                result = action_tools.send_password_reset_link(customer_email or "unknown@example.com")
            elif handler_name == "create_support_ticket":
                issue = action_plan.get("reasoning", "Support request")
                priority = (action_plan.get("priority") or email_context.get("priority") or "MEDIUM").upper()
                result = action_tools.create_support_ticket(customer_id, issue, priority)
            elif handler_name == "notify_human":
                message = action_plan.get("reasoning", "Escalation requested")
                result = action_tools.notify_human(message)
            elif handler_name == "log_action":
                result = action_tools.log_action({"action": action, "email_id": email_id, "plan": action_plan})
            else:
                # default call for mapped handlers
                result = getattr(action_tools, handler_name)(customer_id)

            actions_executed.append({"action": action, "status": "SUCCESS", "result": result})
        except Exception as exc:
            errors.append({"action": action, "error": str(exc)})
            actions_executed.append({"action": action, "status": "FAILED", "result": {"error": str(exc)}})

    overall_status = "SUCCESS" if not errors else "PARTIAL_SUCCESS"

    return {
        "email_id": email_id,
        "actions_executed": actions_executed,
        "overall_status": overall_status,
        "errors": errors,
    }
