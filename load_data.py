import os
import pandas as pd
import sqlite3
import networkx as nx
import json

DATA_DIR = "sap-o2c-data"
DB_PATH = "database.db"

def get_file_from_folder(folder_path):
    for f in os.listdir(folder_path):
        full = os.path.join(folder_path, f)
        if f.endswith(".csv"):
            return full, "csv"
        elif f.endswith(".parquet"):
            return full, "parquet"
        elif f.endswith(".jsonl"):
            return full, "jsonl"
        elif f.endswith(".json"):
            return full, "json"
    return None, None

def load_all_tables():
    conn = sqlite3.connect(DB_PATH)
    tables = {}
    
    if not os.path.exists(DATA_DIR):
        print(f"ERROR: {DATA_DIR} folder not found!")
        return tables, conn
    
    for folder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, folder)
        if os.path.isdir(folder_path):
            file_path, fmt = get_file_from_folder(folder_path)
            if file_path:
                try:
                    if fmt == "parquet":
                        df = pd.read_parquet(file_path)
                    elif fmt == "csv":
                        df = pd.read_csv(file_path)
                    elif fmt == "jsonl":
                        df = pd.read_json(file_path, lines=True)
                    elif fmt == "json":
                        df = pd.read_json(file_path)
                    
                    table_name = folder.replace("-", "_")
                    df.to_sql(table_name, conn, if_exists="replace", index=False)
                    tables[table_name] = df
                    print(f"Loaded: {table_name} ({len(df)} rows)")
                except Exception as e:
                    print(f"Error loading {folder}: {e}")
    
    conn.commit()
    return tables, conn

def build_graph(tables):
    G = nx.DiGraph()
    
    node_configs = {
        "sales_order_headers": ("SalesOrder", "salesOrder"),
        "sales_order_items": ("SalesOrderItem", "salesOrder"),
        "outbound_delivery_items": ("DeliveryItem", "deliveryDocument"),
        "billing_document_items": ("BillingItem", "billingDocument"),
        "business_partners": ("Customer", "businessPartner"),
        "products": ("Product", "product"),
        "plants": ("Plant", "plant"),
        "journal_entry_items_accounts_receivable": ("JournalEntry", "accountingDocument"),
        "payments_accounts_receivable": ("Payment", "accountingDocument"),
    }
    
    for table_name, (node_type, id_col) in node_configs.items():
        if table_name in tables:
            df = tables[table_name]
            if id_col in df.columns:
                for _, row in df.head(100).iterrows():
                    node_id = f"{node_type}_{row[id_col]}"
                    G.add_node(node_id, type=node_type, id=str(row[id_col]),
                              data={k: str(v) for k, v in row.to_dict().items()})
            else:
                print(f"Column '{id_col}' not found in {table_name}. Available: {df.columns.tolist()[:5]}")

    # SalesOrder -> SalesOrderItem
    if "sales_order_items" in tables:
        df = tables["sales_order_items"]
        if "salesOrder" in df.columns:
            for val in df["salesOrder"].head(100).unique():
                G.add_edge(f"SalesOrder_{val}", f"SalesOrderItem_{val}", relation="HAS_ITEM")

    # SalesOrder -> Delivery
    if "outbound_delivery_items" in tables:
        df = tables["outbound_delivery_items"]
        ref_col = next((c for c in ["referenceSDDocument", "salesOrder", "VGBEL"] if c in df.columns), None)
        del_col = next((c for c in ["deliveryDocument", "VBELN"] if c in df.columns), None)
        if ref_col and del_col:
            for _, row in df.head(100).iterrows():
                G.add_edge(f"SalesOrder_{row[ref_col]}", f"DeliveryItem_{row[del_col]}", relation="DELIVERED_VIA")

    # Delivery -> BillingDoc
    if "billing_document_items" in tables:
        df = tables["billing_document_items"]
        ref_col = next((c for c in ["referenceSDDocument", "deliveryDocument", "salesOrder"] if c in df.columns), None)
        bil_col = next((c for c in ["billingDocument", "VBELN"] if c in df.columns), None)
        if ref_col and bil_col:
            for _, row in df.head(100).iterrows():
                G.add_edge(f"DeliveryItem_{row[ref_col]}", f"BillingItem_{row[bil_col]}", relation="BILLED_AS")

    # BillingDoc -> JournalEntry
    if "journal_entry_items_accounts_receivable" in tables:
        df = tables["journal_entry_items_accounts_receivable"]
        ref_col = next((c for c in ["referenceDocument", "billingDocument"] if c in df.columns), None)
        je_col = next((c for c in ["accountingDocument", "BELNR"] if c in df.columns), None)
        if ref_col and je_col:
            for _, row in df.head(100).iterrows():
                G.add_edge(f"BillingItem_{row[ref_col]}", f"JournalEntry_{row[je_col]}", relation="POSTED_TO")

    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def graph_to_json(G):
    nodes = []
    edges = []
    
    for node_id, data in G.nodes(data=True):
        nodes.append({
            "id": node_id,
            "type": data.get("type", "Unknown"),
            "label": f"{data.get('type','?')}\n{data.get('id','?')}",
            "data": {k: str(v) for k, v in data.get("data", {}).items()}
        })
    
    for src, tgt, data in G.edges(data=True):
        edges.append({
            "source": src,
            "target": tgt,
            "relation": data.get("relation", "RELATED_TO")
        })
    
    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    print("Loading tables...")
    tables, conn = load_all_tables()
    print(f"\nLoaded {len(tables)} tables")
    print("Building graph...")
    G = build_graph(tables)
    graph_data = graph_to_json(G)
    with open("graph_data.json", "w") as f:
        json.dump(graph_data, f)
    print("Done! graph_data.json created")
    conn.close()






































# import os
# import pandas as pd
# import sqlite3
# import networkx as nx
# import json

# DATA_DIR = "sap-o2c-data"
# DB_PATH = "database.db"

# def get_csv_from_folder(folder_path):
#     for f in os.listdir(folder_path):
#         if f.endswith(".csv") or f.endswith(".parquet"):
#             return os.path.join(folder_path, f)
#     return None

# def load_all_tables():
#     conn = sqlite3.connect(DB_PATH)
#     tables = {}
    
#     if not os.path.exists(DATA_DIR):
#         print(f"ERROR: {DATA_DIR} folder not found!")
#         return tables, conn
    
#     for folder in os.listdir(DATA_DIR):
#         folder_path = os.path.join(DATA_DIR, folder)
#         if os.path.isdir(folder_path):
#             file_path = get_csv_from_folder(folder_path)
#             if file_path:
#                 try:
#                     if file_path.endswith(".parquet"):
#                         df = pd.read_parquet(file_path)
#                     else:
#                         df = pd.read_csv(file_path)
                    
#                     table_name = folder.replace("-", "_")
#                     df.to_sql(table_name, conn, if_exists="replace", index=False)
#                     tables[table_name] = df
#                     print(f"Loaded: {table_name} ({len(df)} rows)")
#                 except Exception as e:
#                     print(f"Error loading {folder}: {e}")
    
#     conn.commit()
#     return tables, conn

# def build_graph(tables):
#     G = nx.DiGraph()
    
#     # Add nodes
#     node_configs = {
#         "sales_order_headers": ("SalesOrder", "VBELN"),
#         "sales_order_items": ("SalesOrderItem", "VBELN"),
#         "outbound_delivery_headers": ("Delivery", "VBELN"),
#         "outbound_delivery_items": ("DeliveryItem", "VBELN"),
#         "billing_document_headers": ("BillingDoc", "VBELN"),
#         "billing_document_items": ("BillingItem", "VBELN"),
#         "business_partners": ("Customer", "KUNNR"),
#         "products": ("Product", "MATNR"),
#         "plants": ("Plant", "WERKS"),
#         "journal_entry_items_accounts_receivable": ("JournalEntry", "BELNR"),
#         "payments_accounts_receivable": ("Payment", "BELNR"),
#     }
    
#     for table_name, (node_type, id_col) in node_configs.items():
#         if table_name in tables:
#             df = tables[table_name]
#             if id_col in df.columns:
#                 for _, row in df.head(50).iterrows():
#                     node_id = f"{node_type}_{row[id_col]}"
#                     G.add_node(node_id, type=node_type, id=str(row[id_col]), 
#                               data=row.to_dict())
    
#     # Add edges
#     if "sales_order_headers" in tables and "sales_order_items" in tables:
#         so_h = tables["sales_order_headers"]
#         so_i = tables["sales_order_items"]
#         if "VBELN" in so_h.columns and "VBELN" in so_i.columns:
#             for vbeln in so_i["VBELN"].head(50).unique():
#                 G.add_edge(f"SalesOrder_{vbeln}", f"SalesOrderItem_{vbeln}", 
#                           relation="HAS_ITEM")
    
#     if "outbound_delivery_headers" in tables and "billing_document_headers" in tables:
#         del_h = tables["outbound_delivery_headers"]
#         bil_h = tables["billing_document_headers"]
#         common_col = None
#         for col in ["VBELN", "VGBEL", "AUBEL"]:
#             if col in del_h.columns and col in bil_h.columns:
#                 common_col = col
#                 break
#         if common_col:
#             for val in del_h[common_col].head(50).unique():
#                 G.add_edge(f"Delivery_{val}", f"BillingDoc_{val}", 
#                           relation="BILLED_AS")
    
#     print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
#     return G

# def graph_to_json(G):
#     nodes = []
#     edges = []
    
#     for node_id, data in G.nodes(data=True):
#         nodes.append({
#             "id": node_id,
#             "type": data.get("type", "Unknown"),
#             "label": f"{data.get('type','?')}\\n{data.get('id','?')}",
#             "data": {k: str(v) for k, v in data.get("data", {}).items()}
#         })
    
#     for src, tgt, data in G.edges(data=True):
#         edges.append({
#             "source": src,
#             "target": tgt,
#             "relation": data.get("relation", "RELATED_TO")
#         })
    
#     return {"nodes": nodes, "edges": edges}

# if __name__ == "__main__":
#     print("Loading tables...")
#     tables, conn = load_all_tables()
#     print(f"\nLoaded {len(tables)} tables")
#     print("Building graph...")
#     G = build_graph(tables)
#     graph_data = graph_to_json(G)
#     with open("graph_data.json", "w") as f:
#         json.dump(graph_data, f)
#     print("Done! graph_data.json created")
#     conn.close()