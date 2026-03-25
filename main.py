# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import sqlite3
# import json
# import os
# import requests
# from dotenv import load_dotenv
# from load_data import load_all_tables, build_graph, graph_to_json

# load_dotenv()

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load data on startup
# print("Loading data...")
# tables, conn = load_all_tables()
# G = build_graph(tables)
# graph_data = graph_to_json(G)
# print("Ready!")

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# def get_schema():
#     schema = []
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#     for (table,) in cursor.fetchall():
#         cursor.execute(f"PRAGMA table_info({table})")
#         cols = [row[1] for row in cursor.fetchall()]
#         schema.append(f"{table}: {', '.join(cols)}")
#     return "\n".join(schema)

# def query_gemini(user_question, schema):
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
#     prompt = f"""You are a data analyst for a SAP Order-to-Cash business dataset.
# ONLY answer questions about this dataset. If asked anything else, say:
# "This system is designed to answer questions related to the provided dataset only."

# Database schema:
# {schema}

# User question: {user_question}

# First write a valid SQLite SQL query to answer this question.
# Format: SQL: <your query here>
# Then explain what the query does in one line.
# Only use tables and columns from the schema above."""

#     body = {
#         "contents": [{"parts": [{"text": prompt}]}]
#     }
    
#     resp = requests.post(url, json=body)
#     result = resp.json()
    
#     try:
#         return result["candidates"][0]["content"]["parts"][0]["text"]
#     except:
#         return "Sorry, could not generate a response."



# def execute_sql(sql):
#     try:
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         rows = cursor.fetchall()
#         cols = [d[0] for d in cursor.description]
#         return [dict(zip(cols, row)) for row in rows[:20]]
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/graph")
# def get_graph():
#     return graph_data

# @app.post("/query")
# async def query(payload: dict):
#     question = payload.get("question", "")
#     if not question:
#         return {"answer": "Please ask a question."}
    
#     schema = get_schema()
#     llm_response = query_gemini(question, schema)
    
#     # Extract SQL if present
#     sql_result = None
#     if "SQL:" in llm_response:
#         sql_part = llm_response.split("SQL:")[1].strip()
#         sql_query = sql_part.split("\n")[0].strip()
#         sql_result = execute_sql(sql_query)
    
#     return {
#         "answer": llm_response,
#         "data": sql_result
#     }

# @app.get("/health")
# def health():
#     return {"status": "ok"}

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

# **Ctrl+S** save karo.

# ---

# ## STEP 3: Backend restart karo

# Backend wali terminal mein **Ctrl+C** dabaao, phir:
# ```
# uvicorn main:app --reload
# ```

# ---

# ## STEP 4: Test karo

# Browser mein:
# ```
# http://127.0.0.1:8000/health






# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import sqlite3
# import json
# import os
# from dotenv import load_dotenv
# from load_data import load_all_tables, build_graph, graph_to_json

# load_dotenv()

# app = FastAPI()

# # ✅ CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ Load data
# print("Loading data...")
# tables, conn = load_all_tables()
# G = build_graph(tables)
# graph_data = graph_to_json(G)
# print("Ready!")

# # ✅ SQL executor
# def execute_sql(sql):
#     try:
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         rows = cursor.fetchall()
#         cols = [d[0] for d in cursor.description]
#         return [dict(zip(cols, row)) for row in rows[:20]]
#     except Exception as e:
#         return {"error": str(e)}

# # ✅ GRAPH API
# @app.get("/graph")
# def get_graph():
#     return graph_data


# # ✅ QUERY API (RULE-BASED SYSTEM)
# @app.post("/query")
# async def query(payload: dict):
#     question = payload.get("question", "").lower()

#     if not question:
#         return {"answer": "Please ask a question."}

#     # ✅ Guardrail
#     if not any(word in question for word in ["order", "delivery", "product", "billing", "customer"]):
#         return {
#             "answer": "This system is designed to answer questions related to the provided dataset only.",
#             "data": None
#         }

#     # ✅ Deliveries
#     if "delivery" in question:
#         sql = "SELECT COUNT(*) as total_deliveries FROM outbound_delivery_items"
#         data = execute_sql(sql)
#         return {
#             "answer": "Total number of deliveries in the dataset:",
#             "data": data
#         }

#     # ✅ Sales Orders
#     elif "sales order" in question or "order" in question:
#         sql = "SELECT COUNT(*) as total_orders FROM sales_order_headers"
#         data = execute_sql(sql)
#         return {
#             "answer": "Total number of sales orders:",
#             "data": data
#         }

#     # ✅ Top Products
#     elif "product" in question:
#         sql = """
#         SELECT product_id, COUNT(*) as count 
#         FROM sales_order_items 
#         GROUP BY product_id 
#         ORDER BY count DESC 
#         LIMIT 5
#         """
#         data = execute_sql(sql)
#         return {
#             "answer": "Top 5 products based on sales:",
#             "data": data
#         }

#     # ✅ Incomplete flows
#     elif "incomplete" in question or "broken" in question:
#         sql = """
#         SELECT so.sales_order_id
#         FROM sales_order_headers so
#         LEFT JOIN outbound_delivery_items od 
#         ON so.sales_order_id = od.sales_order_id
#         WHERE od.sales_order_id IS NULL
#         LIMIT 10
#         """
#         data = execute_sql(sql)
#         return {
#             "answer": "Sales orders with incomplete flow (no delivery found):",
#             "data": data
#         }

#     # ✅ Billing
#     elif "billing" in question:
#         sql = "SELECT COUNT(*) as total_billing_items FROM billing_document_items"
#         data = execute_sql(sql)
#         return {
#             "answer": "Total number of billing documents:",
#             "data": data
#         }

#     # ✅ Default fallback
#     return {
#         "answer": "Try asking about deliveries, sales orders, products, billing, or incomplete flows.",
#         "data": None
#     }


# # ✅ HEALTH CHECK
# @app.get("/health")
# def health():
#     return {"status": "ok"}