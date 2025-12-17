from typing import TypedDict, List, Optional
from services.models import EmailData, EmailClassificationResult
from db_management.db_models import Claim

class GraphState(TypedDict):
    email: EmailData

    classification_result: Optional[EmailClassificationResult]

    new_claim: Optional[Claim]

    next_step: str
