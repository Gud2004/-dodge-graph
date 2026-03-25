# SAP Order-to-Cash Graph System

A context graph system with LLM-powered natural language query interface built for the Dodge AI FDE Assignment.

## Architecture

- **Backend**: FastAPI (Python) — REST API serving graph data and LLM queries
- **Database**: SQLite — lightweight, file-based, perfect for structured relational queries
- **Graph Engine**: NetworkX — in-memory graph modeling with nodes and edges
- **LLM**: Groq (llama-3.1-8b-instant) — fast free-tier LLM for NL→SQL translation
- **Frontend**: React + Vite + ReactFlow — interactive graph visualization + chat UI

## Why These Choices?

| Component | Choice | Reason |
|---|---|---|
| Database | SQLite | Zero setup, SQL queries, sufficient for dataset size |
| Graph | NetworkX | Perfect for in-memory graph ops, no extra infra |
| LLM | Groq | Free tier, 14k req/day, fast inference |
| Frontend | ReactFlow | Interactive nodes, expandable, clean UI |

## Graph Modeling

Nodes: SalesOrder, SalesOrderItem, DeliveryItem, BillingItem, Customer, Product, Plant, JournalEntry, Payment

Edges:
- SalesOrder → SalesOrderItem (HAS_ITEM)
- SalesOrder → DeliveryItem (DELIVERED_VIA)
- DeliveryItem → BillingItem (BILLED_AS)
- BillingItem → JournalEntry (POSTED_TO)

## LLM Prompting Strategy

1. Guardrail check — keyword matching to reject off-topic queries
2. Schema injection — full DB schema sent to LLM as context
3. Structured output — LLM forced to respond in SQL: ... EXPLANATION: ... format
4. SQL execution — query run on SQLite, results returned as JSON
5. Natural language answer — LLM explanation shown alongside data

## Guardrails

- Keyword whitelist: only dataset-related topics allowed
- Off-topic response: "This system is designed to answer questions related to the provided dataset only."
- SQL execution wrapped in try/catch to prevent injection

## Setup Instructions

### Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn pandas networkx python-multipart openpyxl requests python-dotenv
```

Create `.env` file:
```
GROQ_API_KEY=your_key_here
```
```bash
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Example Queries
- "Which products have the most billing documents?"
- "Show me incomplete sales orders"
- "How many deliveries are there?"
- "Trace billing document flow"
