from __future__ import annotations

import os
import re
from typing import Any, Dict

try:
    from anthropic import Client as AnthropicClient
except Exception:  # pragma: no cover - optional dependency
    AnthropicClient = None

try:
    from dotenv import load_dotenv, find_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None
    find_dotenv = None


class EmailClassifier:
    """Classifies raw email text into structured intent/priority/details.

    If Anthropic API key is present and anthropic is installed, it will call Claude.
    Otherwise a simple heuristic fallback is used for offline testing.
    """

    def __init__(self) -> None:
        if load_dotenv and find_dotenv:
            load_dotenv(find_dotenv(), override=False)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if AnthropicClient and self.api_key:
            self.client = AnthropicClient(api_key=self.api_key)
            self.mode = "claude"
        else:
            self.client = None
            self.mode = "heuristic"

    def get_mode(self) -> str:
        return self.mode

    def _heuristic_classify(self, email_text: str, sender: str | None = None) -> Dict[str, Any]:
        text = (email_text or "").lower()
        intent = "SUPPORT"
        if "refund" in text or "return" in text:
            intent = "REFUND"
        elif "cancel" in text or "cancellation" in text:
            intent = "CANCEL"
        elif "password" in text or "log in" in text or "login" in text:
            intent = "PASSWORD"
        elif "feature" in text or "request" in text:
            intent = "FEATURE"

        priority = "LOW"
        if any(k in text for k in ["urgent", "asap", "immediately"]):
            priority = "HIGH"
        elif any(k in text for k in ["soon", "please"]):
            priority = "MEDIUM"

        # rudimentary key detail extraction for order id and product
        order_match = re.search(r"order\s?#?\s?(\w+)", email_text, re.IGNORECASE)
        product_match = re.search(r"\b(headset|phone|laptop|subscription|account)\b", email_text, re.IGNORECASE)

        key_details: Dict[str, Any] = {}
        if order_match:
            key_details["order_id"] = order_match.group(1)
        if product_match:
            key_details["product"] = product_match.group(1)

        return {
            "intent": intent,
            "priority": priority,
            "customer_email": sender,
            "key_details": key_details,
            "source": "heuristic",
        }

    def classify(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Accepts an email dict with keys like `from`, `subject`, `body`, `id`.

        Returns structured JSON:
        {
          "intent": "REFUND|SUPPORT|CANCEL|PASSWORD|FEATURE",
          "priority": "HIGH|MEDIUM|LOW",
          "customer_email": "...",
          "key_details": {...}
        }
        """
        sender = email.get("from") or email.get("sender")
        subject = email.get("subject", "")
        body = email.get("body", "")
        full_text = f"Subject: {subject}\nBody: {body}"

        if self.client:
            # Call Claude (Anthropic) - keep prompt deterministic and request JSON
            prompt = (
                "You are an assistant that extracts intent, priority, customer email and key details "
                "from a customer support email. Respond only with a JSON object with keys: intent, priority, "
                "customer_email, key_details. Allowed intents: REFUND, SUPPORT, CANCEL, PASSWORD, FEATURE. "
                "Allowed priorities: HIGH, MEDIUM, LOW.\n\nEmail:\n" + full_text
            )

            try:
                resp = self.client.completions.create(
                    model="claude-2.1",  # best-effort default
                    prompt=prompt,
                    max_tokens_to_sample=300,
                )
                text = getattr(resp, "completion", None) or resp.get("completion") or ""
                # try to parse JSON out of the response
                import json

                parsed = json.loads(text.strip())
                parsed["customer_email"] = parsed.get("customer_email") or sender
                parsed["source"] = "claude"
                return parsed
            except Exception:
                # fallback to heuristic on any failure
                return self._heuristic_classify(full_text, sender)

        # no client available -> heuristic fallback
        return self._heuristic_classify(full_text, sender)


if __name__ == "__main__":
    # small self-test when run directly
    sample = {
        "from": "alice@example.com",
        "subject": "I need a refund for my order #12345",
        "body": "Hi, I'd like to return the headset I bought. Order #12345. Please process asap.",
    }
    c = EmailClassifier()
    print(c.classify(sample))
