from langgraph.graph import StateGraph, END
from .app_state import GraphState
from .graph_nodes import (
    classify_node, 
    create_claim_node, 
    handle_general_inquiry_node, 
    index_email_node, 
    final_summary_node,
    identify_client_node
)

from config import OPENAI_API_KEY, DATABASE_URL
from core.services.email_classifier import EmailClassifierService
from core.services.email_index import EmailIndexer
from core.services.chroma_db import ChromaDBCLient
from core.db_management.db_repo import PostgresRepository

#Singleton
db_repo = PostgresRepository(DATABASE_URL)
email_classifier = EmailClassifierService(OPENAI_API_KEY)
email_indexer = EmailIndexer()
email_db = ChromaDBCLient()

def create_app():
    workflow = StateGraph(GraphState)

    workflow.add_node("classify", lambda state: classify_node(state, email_classifier))
    workflow.add_node("identify_client", lambda state: identify_client_node(state, db_repo))
    workflow.add_node("create_claim", lambda state: create_claim_node(state, db_repo))
    workflow.add_node("handle_general_inquiry", handle_general_inquiry_node)
    workflow.add_node("index_email", lambda state: index_email_node(state, email_indexer, email_db))
    workflow.add_node("finish", final_summary_node)

    workflow.set_entry_point("classify")

    workflow.add_conditional_edges(
        "classify",
        lambda state: state["next_step"], 
        {
            "identify_client": "identify_client",
            "index_email": "index_email",
            "handle_general_inquiry": "handle_general_inquiry",
            "finish": "finish"
        }
    )

    workflow.add_edge("identify_client", "create_claim")
    workflow.add_edge("create_claim", "index_email") 
    workflow.add_edge("handle_general_inquiry", "index_email")
    workflow.add_edge("index_email", "finish")
    workflow.add_edge("finish", END)

    return workflow.compile()

app = create_app()