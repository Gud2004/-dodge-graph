# SAP Order-to-Cash Graph Explorer

> "Business data tells a story — this system lets you read it."

A graph-based exploration and natural language query system for SAP O2C data.
Built from scratch in 3 days as part of the Dodge AI FDE Assessment.

## Live Demo
🔗 App: [https://dodge-graph-ten.vercel.app](https://dodge-graph-ten.vercel.app)
⚡ API: [https://dodge-graph-msi1.onrender.com](https://dodge-graph-msi1.onrender.com)

---

## The Problem I Was Solving

SAP O2C data lives in 19 disconnected JSONL files. A business analyst
looking at this data cannot easily answer:
- "Which sales orders were delivered but never billed?"
- "What is the full journey of billing document X?"
- "Which products generate the most billing activity?"

This system solves that — by unifying fragmented data into a graph and
letting anyone query it in plain English.

---

## Architecture
```
┌─────────────────────────────────────────────────────┐
│              FRONTEND (React + Vite)                 │
│  ┌─────────────────────┐  ┌────────────────────────┐│
│  │  Graph Visualization │  │   Chat Interface       ││
│  │  (ReactFlow)         │  │   (NL Query → Answer)  ││
│  │  • 498 nodes         │  │   • SQL transparency   ││
│  │  • 90 edges          │  │   • Guardrail feedback ││
│  │  • Color-coded types │  │   • Example queries    ││
│  │  • Click to inspect  │  │                        ││
│  └─────────────────────┘  └────────────────────────┘│
└──────────────────┬──────────────────┬───────────────┘
                   │ /graph           │ /query
                   ▼                  ▼
┌─────────────────────────────────────────────────────┐
│                BACKEND (FastAPI)                     │
│  ┌──────────────┐   ┌─────────────────────────────┐ │
│  │ Graph Engine  │   │     LLM Query Pipeline      │ │
│  │ (NetworkX)    │   │                             │ │
│  │               │   │  Step 1: GUARDRAIL          │ │
│  │ • O2C flow    │   │   └→ Keyword whitelist      │ │
│  │ • Traversal   │   │   └→ Block off-topic        │ │
│  │               │   │                             │ │
│  │               │   │  Step 2: NL → SQL           │ │
│  │               │   │   └→ Schema injection       │ │
│  │               │   │   └→ Structured output      │ │
│  │               │   │                             │ │
│  │               │   │  Step 3: EXECUTE + ANSWER   │ │
│  │               │   │   └→ SQLite execution       │ │
│  │               │   │   └→ Natural language reply │ │
│  └──────┬────────┘   └──────────────┬──────────────┘ │
│         └──────────────┬────────────┘                 │
│                        ▼                              │
│         ┌──────────────────────────────┐              │
│         │        SQLite Database        │              │
│         │  15 tables · 3000+ rows      │              │
│         │  Built from 19 JSONL files   │              │
│         └──────────────────────────────┘              │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
              Groq API (llama-3.1-8b-instant)
              Free tier · 14,400 req/day
```

---

## What Makes This Different

### 1. I discovered the data format myself
The dataset had no documentation. Opening the files revealed JSONL format
with camelCase column names — not the SAP-standard VBELN format I expected.
I had to inspect each table, map real column names, and rebuild the graph
model accordingly. This informed every JOIN and edge definition.

### 2. I switched LLM providers mid-build and kept going
Started with Gemini. Hit quota limits. Switched to Groq.
The new model (llama3-8b-8192) was deprecated. Switched to llama-3.1-8b-instant.
Each switch required updating the API format, headers, and response parsing.
This is what real engineering looks like — adapting when things break.

### 3. Guardrails before LLM — not inside it
Most implementations ask the LLM to "only answer dataset questions."
I check BEFORE calling the LLM using a keyword whitelist.
Off-topic queries never reach the API — zero cost, zero latency, zero risk.

### 4. Graph + SQL together
NetworkX handles graph structure (nodes, edges, relationships).
SQLite handles analytical queries (COUNT, GROUP BY, JOIN).
The LLM generates SQL — the most reliable structured output format.
This combination gives the best of all three worlds.

---

## Architectural Decisions

### Why SQLite over Neo4j / PostgreSQL?

| Factor | SQLite | Neo4j |
|---|---|---|
| Setup | Zero — embedded in app | Separate server required |
| Query language | SQL — LLM knows it very well | Cypher — less reliable LLM output |
| Dataset size | Perfect for 3000 rows | Overkill |
| Deployment | Single file | Complex infrastructure |

For graph traversal, NetworkX handles it in-memory.
No need for a dedicated graph database at this scale.

### Why Groq over Gemini?
Gemini free tier hit quota limits during development.
Groq offers 14,400 requests/day free — more than sufficient.
llama-3.1-8b-instant is optimized for speed and structured output.

### Why ReactFlow over D3/Cytoscape?
ReactFlow integrates natively with React state.
Node click → inspect metadata panel works out of the box.
Animated edges visually communicate relationships.
MiniMap helps navigate 498 nodes without getting lost.

---

## Graph Modeling

### Nodes — 498 total

| Entity | Source Table | Key Column |
|---|---|---|
| SalesOrder | sales_order_headers | salesOrder |
| SalesOrderItem | sales_order_items | salesOrder |
| DeliveryItem | outbound_delivery_items | deliveryDocument |
| BillingItem | billing_document_items | billingDocument |
| Customer | business_partners | businessPartner |
| Product | products | product |
| Plant | plants | plant |
| JournalEntry | journal_entry_items_AR | accountingDocument |
| Payment | payments_accounts_receivable | accountingDocument |

### Edges — 90 total

| Relationship | From → To | Business Meaning |
|---|---|---|
| HAS_ITEM | SalesOrder → SalesOrderItem | Order contains line items |
| DELIVERED_VIA | SalesOrder → DeliveryItem | Order fulfilled by delivery |
| BILLED_AS | DeliveryItem → BillingItem | Delivery generates invoice |
| POSTED_TO | BillingItem → JournalEntry | Invoice posted to accounts |

### O2C Flow
```
Customer → SalesOrder → SalesOrderItem
                ↓
           DeliveryItem
                ↓
           BillingItem
                ↓
           JournalEntry → Payment
```

---

## LLM Prompting Strategy

### Guardrail (Layer 1 — keyword check, zero LLM cost)
```
Allowed: sales, order, delivery, billing, invoice, payment,
         product, customer, plant, journal, document,
         count, total, show, list, find, how many, which
```
If query matches → pass to LLM
If query doesn't match → block instantly, return standard message

### NL → SQL (Layer 2 — schema-grounded generation)
```
System prompt contains:
- Every table name and column name
- Foreign key relationships
- Output format: SQL: <query> EXPLANATION: <one line>

This eliminates hallucinated table/column names.
The LLM generates SQL it can actually execute.
```

### Execute + Answer (Layer 3)
```
- SQL runs on SQLite
- Results returned as JSON (max 20 rows)
- LLM explanation shown to user
- Raw SQL visible for transparency
```

---

## Guardrails

**What I protect against:**
- General knowledge questions ("capital of France")
- Creative writing requests ("write a poem")
- Completely unrelated topics

**How:**
1. Keyword whitelist check before any LLM call
2. Standard response for blocked queries
3. SQL execution in try/catch — errors never crash the app
4. Results capped at 20 rows

**What gets blocked:**
- ❌ "Tell me a joke" → Blocked instantly
- ❌ "What is Python?" → Blocked instantly
- ✅ "How many sales orders exist?" → Allowed
- ✅ "Show incomplete deliveries" → Allowed

---

## Dataset

- 19 JSONL directories — discovered format by inspection
- 15 tables loaded successfully into SQLite
- 4 tables had unsupported data types (list/dict columns) — handled gracefully
- Column names are camelCase (e.g. salesOrder, soldToParty) — not SAP standard

---

## Setup

### Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn pandas networkx python-multipart openpyxl requests python-dotenv
```

`.env` file:
```
GROQ_API_KEY=your_key_here
```
```bash
uvicorn main:app --reload
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# UI at http://localhost:5173
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/graph` | All nodes + edges as JSON |
| POST | `/query` | NL question → SQL + answer |
| GET | `/health` | Status + table count + node count |

---

## Example Queries

| Question | Tests |
|---|---|
| "Which products have the most billing documents?" | Aggregation + JOIN |
| "Show me incomplete sales orders" | Status filtering |
| "How many deliveries are there?" | Simple COUNT |
| "Trace the flow of a billing document" | Relationship traversal |
| "Tell me a joke" | Guardrail — blocked ✅ |

---

## Project Structure
```
dodge-graph/
├── main.py              # FastAPI app — /graph, /query, /health
├── load_data.py         # JSONL ingestion → SQLite + NetworkX graph
├── .env                 # API keys (gitignored)
├── frontend/
│   ├── src/
│   │   └── App.jsx      # React — graph viz + chat interface
│   └── package.json
├── sap-o2c-data/        # 19 JSONL entity directories (gitignored)
├── claude-session.txt   # AI coding session logs
└── README.md
```

---

## Tech Stack

| Layer | Tech | Why |
|---|---|---|
| Backend | FastAPI | Async, clean, auto docs |
| Database | SQLite | Zero setup, SQL, portable |
| Graph | NetworkX | In-memory, no infra |
| LLM | Groq llama-3.1-8b-instant | Free, fast, reliable |
| Frontend | React + Vite | Fast dev, simple build |
| Graph UI | ReactFlow | Native React, interactive |
| Deploy | Render + Vercel | Free tier, GitHub integration |
