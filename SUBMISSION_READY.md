Submission Ready

Project overview
- End-to-end Email Agent that classifies intent, retrieves policy context with RAG, decides actions, and executes mock tools.

How to run
- python test_agent.py

What it does (5 phases)
1. Classify email intent and priority
2. Retrieve top policy docs from Chroma vector DB
3. Decide action plan with reasoning and confidence
4. Execute mock tools and log actions
5. Generate demo outputs (final_report.json, demo_output.txt)

Results
- 5/5 emails processed successfully in the latest demo run

Tech stack
- Claude (optional for classification and decision)
- ChromaDB (vector search)
- RAG pipeline
