from __future__ import annotations

import json
import time
from pathlib import Path

from agents.knowledge_retriever import KnowledgeRetriever
from agents.email_classifier import EmailClassifier
from agents.decision_maker import make_decision
from agents.executor import execute_actions

try:
    from dotenv import load_dotenv, find_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None
    find_dotenv = None
from data.knowledge_base import KNOWLEDGE_DOCUMENTS
from data.mock_emails import MOCK_EMAILS


def _format_seconds(value: float) -> str:
    return f"{value:.1f}s"


def run_full_demo(write_outputs: bool = True) -> dict:
    if load_dotenv and find_dotenv:
        load_dotenv(find_dotenv(), override=False)
    # Phase 2: classify incoming emails
    classifier = EmailClassifier()
    print(f"EmailClassifier mode: {classifier.get_mode()}")

    # Phase 3: index knowledge base and run semantic retrieval
    retriever = KnowledgeRetriever()
    indexed_count = retriever.build_index(KNOWLEDGE_DOCUMENTS, reset=True)

    report: dict = {
        "indexed_documents": indexed_count,
        "emails": [],
    }

    timings = {"classify": 0.0, "retrieve": 0.0, "decide": 0.0, "execute": 0.0}
    decision_counts = {"APPROVE": 0, "DENY": 0, "ESCALATE": 0}
    action_counts: dict[str, int] = {}
    email_summaries = []
    full_results = []
    similarity_scores = []

    for email in MOCK_EMAILS:
        t0 = time.perf_counter()
        classification = classifier.classify(email)
        timings["classify"] += time.perf_counter() - t0

        query = f"Subject: {email['subject']}\nBody: {email['body']}"
        t0 = time.perf_counter()
        top_docs = retriever.retrieve(query, top_k=3)
        timings["retrieve"] += time.perf_counter() - t0
        # Phase 4: decision maker
        t0 = time.perf_counter()
        decision = make_decision(classification, top_docs)
        timings["decide"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        execution = execute_actions(decision, email | {"priority": classification.get("priority")})
        timings["execute"] += time.perf_counter() - t0

        # summary stats
        decision_key = decision.get("decision", "ESCALATE")
        decision_counts[decision_key] = decision_counts.get(decision_key, 0) + 1
        for action_item in execution.get("actions_executed", []):
            action_name = action_item.get("action")
            if action_name:
                action_counts[action_name] = action_counts.get(action_name, 0) + 1

        # similarity scoring (avg of available scores per email)
        scores = [d.get("score") for d in top_docs if d.get("score") is not None]
        if scores:
            similarity_scores.append(sum(scores) / len(scores))

        email_summaries.append(
            {
                "id": len(email_summaries) + 1,
                "sender": email.get("from"),
                "intent": classification.get("intent"),
                "decision": decision.get("decision"),
                "actions_count": len(execution.get("actions_executed", [])),
                "status": "SUCCESS" if execution.get("overall_status") == "SUCCESS" else "FAILED",
            }
        )

        full_results.append(
            {
                "raw_email": email,
                "classification": classification,
                "retrieval": top_docs,
                "decision": decision,
                "execution": execution,
            }
        )

        report["emails"].append(
            {
                "email_id": email["id"],
                "from": email.get("from"),
                "subject": email["subject"],
                "classification": classification,
                "top_docs": top_docs,
                "decision": decision,
                "execution": execution,
            }
        )
    total_emails = len(MOCK_EMAILS)
    successful = sum(1 for e in email_summaries if e["status"] == "SUCCESS")
    failed = total_emails - successful
    avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0

    final_report = {
        "total_emails_processed": total_emails,
        "successful": successful,
        "failed": failed,
        "decisions": decision_counts,
        "actions_executed": action_counts,
        "execution_times": {
            "classify": _format_seconds(timings["classify"]),
            "retrieve": _format_seconds(timings["retrieve"]),
            "decide": _format_seconds(timings["decide"]),
            "execute": _format_seconds(timings["execute"]),
        },
        "vector_db_performance": {
            "total_queries": total_emails,
            "avg_similarity": round(avg_similarity, 2),
            "top_3_docs_retrieved": sum(len(r["retrieval"]) for r in full_results),
        },
        "emails_processed": email_summaries,
        "full_results": full_results,
    }

    demo_lines = [
        "EMAIL AGENT - DEMO REPORT",
        f"Total Emails Processed: {total_emails}",
        f"Success Rate: {int((successful / total_emails) * 100) if total_emails else 0}%",
        f"Vector DB Queries: {total_emails}",
        f"Avg Semantic Similarity: {round(avg_similarity, 2)}",
        "",
    ]

    for idx, item in enumerate(full_results, start=1):
        email = item["raw_email"]
        classification = item["classification"]
        decision = item["decision"]
        execution = item["execution"]

        demo_lines.append(f"EMAIL {idx}: {email.get('subject', 'No subject')}")
        demo_lines.append(f"From: {email.get('from')}")
        demo_lines.append(
            f"Intent: {classification.get('intent')} (priority: {classification.get('priority')})"
        )
        demo_lines.append("Retrieved Policies (RAG with Vector DB):")
        for doc in item["retrieval"]:
            score = doc.get("score")
            score_text = f"{score:.2f}" if isinstance(score, (int, float)) else "N/A"
            demo_lines.append(f"- \"{doc.get('text')}\" (similarity: {score_text})")
        demo_lines.append("")
        demo_lines.append(f"Decision: {decision.get('decision')}")
        demo_lines.append(f"Reasoning: {decision.get('reasoning')}")
        demo_lines.append("Actions Executed:")
        for action in execution.get("actions_executed", []):
            status = action.get("status")
            action_name = action.get("action")
            result = action.get("result")
            demo_lines.append(f"- {action_name} [{status}] -> {result}")
        demo_lines.append("")

    if write_outputs:
        root = Path(__file__).resolve().parent
        (root / "final_report.json").write_text(json.dumps(final_report, indent=2), encoding="utf-8")
        (root / "demo_output.txt").write_text("\n".join(demo_lines), encoding="utf-8")

    report["final_report"] = final_report
    report["demo_output"] = "\n".join(demo_lines)
    return report


if __name__ == "__main__":
    output = run_full_demo(write_outputs=True)
    print(json.dumps(output["final_report"], indent=2))
