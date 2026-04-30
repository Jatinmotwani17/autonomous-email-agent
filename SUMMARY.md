Email Agent Summary

What this agent does
- Reads incoming customer emails and extracts intent, priority, and key details.
- Retrieves relevant policies using semantic RAG with a Chroma vector database.
- Makes a decision (approve/deny/escalate) with a confidence score.
- Executes mock actions and logs all actions to JSON.

Tech stack
- Python
- ChromaDB for vector retrieval
- Anthropic Claude (optional) for classification and decision reasoning

Phases 1-5 overview
1. Foundation setup and mock data
2. Email classifier (intent, priority, key details)
3. RAG retrieval via semantic vector search
4. Decision maker for action planning
5. Executor that performs actions and logs results

Key achievements
- End-to-end pipeline from email to action execution
- Vector DB-powered retrieval for policy context
- Structured outputs for testing and reporting

How RAG + Vector DB powers decisions
- Email content is embedded and matched against policy documents.
- Top relevant policies are provided to the decision maker.
- Decisions and actions are grounded in retrieved context.
