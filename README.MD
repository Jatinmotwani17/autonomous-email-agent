AGENT EMAIL SYSTEM - COMPLETE PLAN
WHAT WE'RE BUILDING
Email Agent that:
1. Reads emails
2. Understands intent (refund, support, cancellation, etc.)
3. Retrieves relevant knowledge (RAG)
4. MAKES DECISIONS (what to do)
5. TAKES ACTIONS (process refund, create ticket, send email)
6. MONITORS execution
7. LOGS everything

Result: Fully automated email handling

📋 PROJECT PHASES (4-5 hours total)
PHASE 1: Foundation Setup (30 min)

 Create Python project structure
 Install dependencies (Claude API, dotenv)
 Create mock knowledge base
 Create mock email inbox
 Setup logging

Output: Project skeleton ready

PHASE 2: Email Understanding (1 hour)

 Create email parser
 Use Claude to understand intent
 Extract key info (customer, issue, urgency)
 Classify email type (refund, support, cancellation, etc.)

Output: "Email classifier" - knows what each email is asking for

PHASE 3: RAG - Knowledge Retrieval (1 hour)

 Create knowledge base (policies, FAQs, rules)
 Build vector database in Chroma
 Convert knowledge docs into embeddings and store vectors
 Convert incoming email into embedding
 Run semantic similarity search
 Retrieve top 3 most relevant docs for decision making

Output: "Semantic policy retriever" - finds most relevant rules using vector similarity

PHASE 4: Decision & Action Planning (1 hour)

 Create action planner (decides what to do)
 Define available tools/actions:

Process refund
Create support ticket
Reset password
Cancel subscription
Send response email
Log action


 Plan sequence of actions

Output: "Action planner" - decides what actions to take

PHASE 5: Execution & Monitoring (1 hour)

 Create tool executors (actually do the actions)
 Add error handling
 Add monitoring (track success/failure)
 Log all actions to JSON
 Generate summary report

Output: "Full agent" - actually executes everything

PHASE 6: Testing & Demo (30 min)

 Test with multiple email types
 Generate demo report
 Create GitHub repo
 Write README

Output: Working demo ready to show Urja

🏗️ PROJECT STRUCTURE
email-agent/
├── main.py (main agent orchestrator)
├── agents/
│   ├── email_classifier.py (understand intent)
│   ├── knowledge_retriever.py (RAG - get context)
│   ├── decision_maker.py (plan actions)
│   └── executor.py (take actions)
├── tools/
│   ├── refund_tool.py
│   ├── ticket_tool.py
│   ├── password_tool.py
│   ├── cancel_tool.py
│   └── email_tool.py
├── data/
│   ├── knowledge_base.py (policies, rules)
│   ├── mock_emails.py (test emails)
│   └── mock_database.py (customer data)
├── logs/
│   └── actions.json (all actions executed)
├── .env (API keys)
├── requirements.txt
├── README.md
└── results.json (final report)

🔄 AGENT FLOW DIAGRAM
Email Arrives
    ↓
┌─────────────────────────────┐
│ PHASE 1: CLASSIFIER         │
│ What is this email asking?  │
│ Intent: REFUND/SUPPORT/etc. │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ PHASE 2: RAG RETRIEVAL      │
│ Chroma semantic retrieval   │
│ Get top 3 similar policies  │
│ Get customer context        │
│ Get eligibility rules       │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ PHASE 3: DECISION MAKER     │
│ Decide: Can we help?        │
│ Plan: What actions needed?  │
│ Sequence: In what order?    │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ PHASE 4: EXECUTOR           │
│ Execute Action 1: Process   │
│ Execute Action 2: Update DB │
│ Execute Action 3: Send mail │
│ Monitor: Success? Error?    │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ PHASE 5: LOGGER             │
│ Log all actions taken       │
│ Save to JSON                │
│ Generate report             │
└─────────────────────────────┘
    ↓
Done! Zero human work.

📊 SAMPLE EMAIL TYPES WE'LL HANDLE
Email TypeIntentActions"I want a refund"REFUNDCheck eligibility → Process refund → Send confirmation"My password is lost"PASSWORD_RESETGenerate reset link → Send email"I want to cancel"CANCELLATIONVerify account → Cancel sub → Send confirmation"Your product is broken"SUPPORT_TICKETCreate ticket → Assign to team → Send ACK"Where's my order?"TRACKINGLook up order → Get status → Send tracking"Feature request: dark mode"FEATURE_REQUESTLog request → Add to backlog → Send ACK

🗄️ KNOWLEDGE BASE (What we'll store)
pythonKNOWLEDGE_BASE = {
    "refund_policy": "60 days from purchase",
    "refund_eligibility": "Product unused, original packaging",
    "refund_processing_time": "3-5 business days",
    "cancellation_policy": "Cancel anytime",
    "password_reset": "Send link via email",
    "support_response_time": "24 hours",
    "feature_request_process": "Add to backlog, quarterly review",
    ...
}

Each policy chunk is stored in Chroma as a document with metadata and an embedding vector.

Example retrieval behavior:
1. Email text -> embedding
2. Chroma similarity query
3. Return top 3 relevant policy documents

python
results = collection.query(
    query_texts=[email_text],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)

🛠️ TOOLS WE'LL CREATE
pythonclass RefundTool:
    def execute(self, customer_id, amount):
        # Actually process refund
        return {"status": "success", "refund_id": "REF-123"}

class EmailTool:
    def execute(self, to, subject, body):
        # Actually send email
        return {"status": "sent", "email_id": "EMAIL-456"}

class DatabaseTool:
    def execute(self, action, data):
        # Actually update database
        return {"status": "updated"}

# ... etc for each tool

How to Run the Demo

1) Install dependencies

```powershell
python -m pip install -r requirements.txt
```

2) Run the end-to-end demo

```powershell
python test_agent.py
```

Expected output
- Prints a JSON summary to the console
- Writes final_report.json and demo_output.txt in the project root
- Appends action logs to logs/actions.json

What each phase does
1. Phase 2: Classifies the email (intent, priority, key details)
2. Phase 3: Retrieves top 3 relevant policy docs via Chroma vector search
3. Phase 4: Decides the action plan with reasoning and confidence
4. Phase 5: Executes mock tools and logs actions
5. Phase 6: Generates final_report.json and demo_output.txt

Phase 6 Demo Results
- final report: [final_report.json](final_report.json)
- demo output: [demo_output.txt](demo_output.txt)
- action logs: [logs/actions.json](logs/actions.json)

Sample output (from final_report.json)
```json
{
    "total_emails_processed": 5,
    "successful": 5,
    "failed": 0,
    "decisions": {
        "APPROVE": 5,
        "DENY": 0,
        "ESCALATE": 0
    }
}
```
