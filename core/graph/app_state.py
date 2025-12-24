from typing import TypedDict, List, Optional
from core.services.models import EmailData, EmailClassificationResult
from core.db_management.db_models import Claim

class GraphState(TypedDict):
    email: EmailData
    
    classification_result: Optional[EmailClassificationResult]
    
    client_id: Optional[int]
    client_name_db: Optional[str]
    
    new_claim: Optional[Claim]
    
    next_step: str