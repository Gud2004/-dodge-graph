from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import requests
from dotenv import load_dotenv
from load_data import load_all_tables, build_graph, graph_to_json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading data...")
tables, conn = load_all_tables()
G = build_graph(tables)
graph_data = graph_to_json(G)
print("Ready!")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_schema():
    schema = []
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for (table,) in cursor.fetchall():
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cursor.fetchall()]
        schema.append(f"{table}: {', '.join(cols)}")
    return "\n".join(schema)

def query_gemini(user_question, schema):
    ALLOWED_TOPICS = ["sales", "order", "delivery", "billing", "invoice", "payment", 
                      "product", "customer", "plant", "journal", "dataset", "document",
                      "how many", "which", "show", "list", "find", "count", "total"]
    
    question_lower = user_question.lower()
    is_relevant = any(topic in question_lower for topic in ALLOWED_TOPICS)
    
    if not is_relevant:
        return "This system is designed to answer questions related to the provided dataset only."

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"""You are a data analyst for a SAP Order-to-Cash business dataset.
ONLY answer questions about this dataset. If asked anything unrelated, say exactly:
"This system is designed to answer questions related to the provided dataset only."

Database schema:
{schema}

User question: {user_question}

Write a valid SQLite SQL query to answer this question.
Format your response exactly like this:
SQL: SELECT ... FROM ...
EXPLANATION: one line explanation

Only use tables and columns that exist in the schema above.
Do not use markdown code blocks."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=30)
        result = resp.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            return f"API Error: {result['error']['message']}"
        else:
            return f"Unexpected: {str(result)[:200]}"
    except Exception as e:
        return f"Request failed: {str(e)}"
    
def execute_sql(sql):
    try:
        sql = sql.strip().rstrip(";")
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in rows[:20]]
    except Exception as e:
        return {"error": str(e)}

@app.get("/graph")
def get_graph():
    return graph_data

@app.post("/query")
async def query(payload: dict):
    question = payload.get("question", "")
    if not question:
        return {"answer": "Please ask a question.", "data": None}
    
    schema = get_schema()
    llm_response = query_gemini(question, schema)
    
    sql_result = None
    if "SQL:" in llm_response:
        try:
            sql_part = llm_response.split("SQL:")[1].strip()
            sql_query = sql_part.split("\n")[0].strip()
            if sql_query:
                sql_result = execute_sql(sql_query)
        except:
            pass
    
    return {"answer": llm_response, "data": sql_result}

@app.get("/health")
def health():
    return {"status": "ok", "tables": len(tables), "nodes": G.number_of_nodes()}


@app.get("/")
def root():
    return {"message": "SAP O2C Graph API is running 🚀"}