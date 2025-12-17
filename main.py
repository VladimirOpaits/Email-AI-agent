from langgraph.graph import StateGraph, END
from graph.app_state import GraphState
from graph.graph_nodes import (
    classify_node, 
    create_claim_node, 
    handle_general_inquiry_node, 
    index_email_node, 
    final_summary_node
)

from services.email_ingest import EmailClientFlanker
from services.email_index import EmailIndexer
from services.chroma_db import ChromaDBCLient
from services.email_classifier import EmailClassifierService
from db_management.db_repo import PostgresRepository
from config import OPENAI_API_KEY

from datetime import datetime

from config import DATABASE_URL

def convert_iso_to_imap(iso_date_str: str) -> str:
    dt = datetime.fromisoformat(iso_date_str.split('+')[0])
    return dt.strftime('%d-%b-%Y')

db_repo = PostgresRepository(DATABASE_URL)
db_repo.create_tables()

email_client = EmailClientFlanker("imap.gmail.com", "emailaicorporation@gmail.com", "uzxg yero fsgj rfws", "INBOX", ssl=True)
email_classifier = EmailClassifierService(OPENAI_API_KEY)
email_indexer = EmailIndexer()
email_db = ChromaDBCLient()

email_db.clear_db()

workflow = StateGraph(GraphState)

workflow.add_node("classify", lambda state: classify_node(state, email_classifier))
workflow.add_node("create_claim", lambda state: create_claim_node(state, db_repo))
workflow.add_node("handle_general_inquiry", handle_general_inquiry_node)
workflow.add_node("index_email", lambda state: index_email_node(state, email_indexer, email_db))
workflow.add_node("finish", final_summary_node)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    lambda state: state["next_step"], 
    {
        "create_claim": "create_claim",
        "index_email": "index_email",
        "handle_general_inquiry": "handle_general_inquiry"
    }
)

workflow.add_edge("create_claim", "index_email") 
workflow.add_edge("handle_general_inquiry", "index_email")
workflow.add_edge("index_email", "finish")
workflow.add_edge("finish", END)

app = workflow.compile() 

new_emails = email_client.fetch_new(convert_iso_to_imap("2025-12-01T09:07:20+01:00"))

print("--- STARTING CLAIM PROCESSING GRAPH ---")
for email in new_emails:
    print(f"\n===========================================")
    print(f"Processing Email: {email.subject}")
    
    initial_state = GraphState(
        email=email,
        classification_result=None,
        new_claim=None,
        next_step="classify" 
    )
    
    app.invoke(initial_state)

print("\n--- BATCH PROCESSING COMPLETE ---")