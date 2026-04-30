from __future__ import annotations

import os
from typing import Any, Dict, List

try:
    from anthropic import Client as AnthropicClient
except Exception:
    AnthropicClient = None

try:
    from dotenv import load_dotenv, find_dotenv
except Exception:
    load_dotenv = None
    find_dotenv = None


def _heuristic_refund_decision(classified: Dict[str, Any], docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Look for explicit refund eligibility phrases in retrieved docs
    texts = " ".join(d.get("text", "") for d in docs).lower()

    reasoning_parts = []
    eligible_policy = False
    if "60" in texts or "60 days" in texts or "refund eligibility" in texts:
        eligible_policy = True
        reasoning_parts.append("Policy allows refunds within 60 days or specifies refund eligibility.")

    # Basic customer info checks (we don't have purchase date), so rely on available key_details
    key_details = classified.get("key_details", {}) or {}
    has_order = bool(key_details.get("order_id"))
    if has_order:
        reasoning_parts.append("Customer provided an order id.")

    # Decide
    if eligible_policy and has_order:
        decision = "APPROVE"
        actions = ["process_refund", "send_confirmation_email", "log_action"]
        confidence = 0.8
        reasoning_parts.append("Policy and order information indicate eligibility.")
    elif eligible_policy and not has_order:
        decision = "ESCALATE"
        actions = ["create_support_ticket", "notify_human", "log_action"]
        confidence = 0.5
        reasoning_parts.append("Policy suggests refund may be allowed but missing order information.")
    else:
        decision = "DENY"
        actions = ["send_denial_email", "offer_support", "log_action"]
        confidence = 0.7
        reasoning_parts.append("Policy does not indicate eligibility or insufficient evidence.")

    return {
        "decision": decision,
        "reasoning": " ".join(reasoning_parts),
        "actions": actions,
        "confidence": confidence,
    }


def make_decision(classified_email: Dict[str, Any], retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Produce a decision dict from classified email and retrieved docs.

    Tries Claude (Anthropic) if available; otherwise uses heuristics per intent.
    """
    if load_dotenv and find_dotenv:
        load_dotenv(find_dotenv(), override=False)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if AnthropicClient and api_key:
        client = AnthropicClient(api_key=api_key)
        # build a concise prompt including classification and retrieved docs
        import json

        prompt = (
            "You are an assistant that makes a decision for a customer email. "
            "Input is JSON with keys 'classified' and 'retrieved_docs'. "
            "Return only valid JSON with keys: decision (APPROVE|DENY|ESCALATE), reasoning, actions (list), confidence (0.0-1.0).\n\n"
            + "Input:\n"
            + json.dumps({"classified": classified_email, "retrieved_docs": retrieved_docs}, indent=2)
        )

        try:
            resp = client.completions.create(model="claude-2.1", prompt=prompt, max_tokens_to_sample=400)
            text = getattr(resp, "completion", None) or resp.get("completion") or ""
            import json as _json

            parsed = _json.loads(text.strip())
            return parsed
        except Exception:
            # fall through to heuristics
            pass

    # Heuristic decision logic
    intent = (classified_email.get("intent") or "").upper()

    if intent == "REFUND":
        return _heuristic_refund_decision(classified_email, retrieved_docs)

    if intent in ("SUPPORT", "ISSUE"):
        reason = "Support request - create ticket and acknowledge customer."
        return {
            "decision": "APPROVE",
            "reasoning": reason,
            "actions": ["create_support_ticket", "assign_priority", "send_acknowledgement_email", "log_action"],
            "confidence": 0.9,
        }

    if intent == "CANCEL" or intent == "CANCELLATION":
        # look for subscription mention in docs
        texts = " ".join(d.get("text", "") for d in retrieved_docs).lower()
        if "cancel anytime" in texts or "cancel" in texts:
            return {
                "decision": "APPROVE",
                "reasoning": "Cancellation policy allows cancel; active subscription likely.",
                "actions": [
                    "process_cancellation",
                    "process_refund_if_applicable",
                    "send_confirmation_email",
                    "log_action",
                ],
                "confidence": 0.8,
            }
        else:
            return {
                "decision": "DENY",
                "reasoning": "No active subscription evidence found.",
                "actions": ["send_email_no_active_sub", "log_action"],
                "confidence": 0.6,
            }

    if intent in ("PASSWORD", "PASSWORD_RESET", "TECHNICAL"):
        return {
            "decision": "APPROVE",
            "reasoning": "Password/technical issue - provide reset and create ticket.",
            "actions": ["send_password_reset_link", "create_support_ticket", "log_action"],
            "confidence": 0.95,
        }

    if intent == "FEATURE" or intent == "FEATURE_REQUEST":
        return {
            "decision": "APPROVE",
            "reasoning": "Feature request logged for backlog.",
            "actions": ["log_feature_request", "add_to_backlog", "send_acknowledgement_email", "log_action"],
            "confidence": 0.7,
        }

    # default: escalate
    return {
        "decision": "ESCALATE",
        "reasoning": "Could not map intent confidently; escalate to human.",
        "actions": ["create_support_ticket", "notify_human", "log_action"],
        "confidence": 0.5,
    }


if __name__ == "__main__":
    # small smoke test
    sample_classified = {"intent": "REFUND", "priority": "HIGH", "customer_email": "bob@example.com", "key_details": {"order_id": "123"}}
    sample_docs = [{"id": "refund_policy_window", "text": "Refund policy allows refunds within 60 days from purchase date."}]
    print(make_decision(sample_classified, sample_docs))
