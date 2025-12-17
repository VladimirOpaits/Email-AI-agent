from .app_state import GraphState
from services.email_classifier import EmailClassifierService
from db_management.db_repo import PostgresRepository
from services.models import EmailCategory
from services.email_index import EmailIndexer
from services.chroma_db import ChromaDBCLient

from datetime import datetime, timezone

def classify_node(state: GraphState, classifier: EmailClassifierService) -> GraphState:
    email = state["email"]

    classification_result = classifier.classify_email(email)

    if classification_result.category == EmailCategory.INSURANCE_CLAIM:
        next_step = "create_claim"
    else:
        next_step = "finish"

    return {
        "classification_result": classification_result,
        "next_step": next_step
    }

def create_claim_node(state: GraphState, db_repo: PostgresRepository) -> GraphState:
    classification = state["classification_result"]
    email = state["email"]

    if not classification or not classification.extracted_data:
        return {
            "new_claim": None,
            "next_step": "finish"
        }
    
    extracted = classification.extracted_data

    claim_kwargs = {
        "client_name": extracted.client_name,
        "policy_id": extracted.policy_id,
        "incident_date": extracted.incident_date,
        "incident_summary": extracted.incident_description_summary,
        "source_email_id": email.message_id,
        "created_at": datetime.now(timezone.utc), 
        "status": "NEW"
    }

    claim_kwargs = {k: v for k, v in claim_kwargs.items() if v is not None}

    new_claim = None
    for session in db_repo.get_db_session():
        existing_claim = db_repo.get_claim_by_email_id(session, email.message_id)
        if existing_claim:
            return {"new_claim": existing_claim, "next_step": "finish"}
        
        try:
            new_claim = db_repo.create_claim(session, **claim_kwargs)
            print(f"Created new claim with ID: {new_claim.id}")
        except Exception as e:
            print(f"Error creating claim: {e}")
            return {"new_claim": None, "next_step": "finish"}
        
        break

    return {
        "new_claim": new_claim,
        "next_step": "index_email"
    }

def handle_general_inquiry_node(state: GraphState) -> GraphState:
    print("Handling general inquiry. No claim created.")
    return {"next_step": "index_email"}


def index_email_node(state: GraphState, indexer: EmailIndexer, db_client: ChromaDBCLient) -> GraphState:
    email = state["email"]
    classification = state["classification_result"]
    request_type = classification.category if classification else "unknown"
    try:
        indexer.index_email(email, db_client)
        print(f"Indexed email ID {email.id} as {request_type}.")
    except Exception as e:
        print(f"Error indexing email ID {email.id}: {e}")

    return {"next_step": "finish"}

def final_summary_node(state: GraphState) -> GraphState:
    if state["new_claim"]:
        print(f"Claim created successfully: ID {state['new_claim'].id}, Policy: {state['new_claim'].policy_id}")
    elif state["classification_result"]:
        print(f"Email classified as: {state['classification_result'].category}")
    else:
        print("No action taken.")
    return state