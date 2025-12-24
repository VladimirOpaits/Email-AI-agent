from .app_state import GraphState
from core.services.email_classifier import EmailClassifierService
from core.db_management.db_repo import PostgresRepository
from core.services.models import EmailCategory
from core.services.email_index import EmailIndexer
from core.services.chroma_db import ChromaDBCLient
from datetime import datetime, timezone

def classify_node(state: GraphState, classifier: EmailClassifierService) -> GraphState:
    email = state["email"]
    classification_result = classifier.classify_email(email)
    
    if classification_result.category == EmailCategory.INSURANCE_CLAIM:
        next_step = "identify_client"
    else:
        next_step = "finish"

    return {
        "classification_result": classification_result,
        "next_step": next_step
    }

def identify_client_node(state: GraphState, db_repo: PostgresRepository) -> GraphState:
    email_obj = state["email"]
    sender_email = email_obj.sender
    extracted = state["classification_result"].extracted_data
    
    client_id = None
    client_name_db = None

    for session in db_repo.get_db_session():
        client = db_repo.get_client_by_email(session, sender_email)
        
        if not client and extracted and extracted.policy_id:
            policy = db_repo.get_policy_by_number(session, extracted.policy_id)
            if policy:
                client = db_repo.get_client_by_id(session, policy.client_id)
        
        if client:
            client_id = client.id
            client_name_db = client.full_name
        break

    return {
        "client_id": client_id,
        "client_name_db": client_name_db,
        "next_step": "create_claim"
    }

def create_claim_node(state: GraphState, db_repo: PostgresRepository) -> GraphState:
    classification = state["classification_result"]
    email = state["email"]
    client_id = state.get("client_id")

    if not classification or not classification.extracted_data:
        return {"next_step": "finish"}
    
    extracted = classification.extracted_data

    claim_kwargs = {
        "client_id": client_id,
        "client_name": extracted.client_name,
        "policy_id": extracted.policy_id,
        "incident_date": extracted.incident_date,
        "incident_summary": extracted.incident_description_summary,
        "source_email_id": email.message_id,
        "status": "NEW" if client_id else "UNIDENTIFIED"
    }

    claim_kwargs = {k: v for k, v in claim_kwargs.items() if v is not None}

    new_claim = None
    for session in db_repo.get_db_session():
        existing_claim = db_repo.get_claim_by_email_id(session, email.message_id)
        if existing_claim:
            return {"new_claim": existing_claim, "next_step": "index_email"}
        
        try:
            new_claim = db_repo.create_claim(session, **claim_kwargs)
        except Exception as e:
            print(f"Error: {e}")
            return {"next_step": "finish"}
        break

    return {"new_claim": new_claim, "next_step": "index_email"}

def index_email_node(state: GraphState, indexer: EmailIndexer, db_client: ChromaDBCLient) -> GraphState:
    email = state["email"]
    try:
        indexer.index_email(email, db_client)
    except Exception as e:
        print(f"Error: {e}")
    return {"next_step": "finish"}

def final_summary_node(state: GraphState) -> GraphState:
    return state