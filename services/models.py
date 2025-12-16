from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from dataclasses import dataclass

class EmailCategory(str, Enum):
    INSURANCE_CLAIM = "InsuranceClaim"
    GENERAL_INQUIRY = "GeneralInquiry"
    CLAIM_DIALOGUE = "ClaimDialogue" 

class EmailData(BaseModel):
    id: str
    date: str = Field(description="Date of the email in ISO 8601 format.")
    body: str
    subject: str
    attachments: List[Dict[str, Any]]
    
    from_address: str = Field(alias="from")
    to_addresses: str = Field(alias="to")
    message_id: str
    in_reply_to: str
    references: str
    
    request_type: Optional[EmailCategory] = None

    class Config:
        populate_by_name = True

class ClaimData(BaseModel):
    client_name: Optional[str] = Field(description="Full name of the client submitting the claim.")
    policy_id: Optional[str] = Field(description="The policy identification number mentioned in the email.")
    incident_date: Optional[str] = Field(description="The date of the incident (e.g., 'yesterday', '2025-12-10').")
    incident_description_summary: Optional[str] = Field(description="A brief, one-sentence summary of the incident.")

class EmailClassificationResult(BaseModel):
    category: EmailCategory = Field(
        description="Must be one of: InsuranceClaim, GeneralInquiry or Claim Dialogue."
    )
    explanation: str = Field(
        description="A brief explanation of why this category was chosen."
    )
    
    extracted_data: Optional[ClaimData] = Field(
        None, description="Claim data, extracted if = InsuranceClaim."
    )

class SimpleClassificationResult(BaseModel):
    category: EmailCategory = Field(description="Must be one of: InsuranceClaim, GeneralInquiry or Claim Dialogue.")
    explanation: str = Field(description="A brief explanation.")

@dataclass
class ChunkMetadata:
    source: str
    document_type: str 
    date: str
    
    # email
    subject: Optional[str]
    sender: Optional[str]
    to: Optional[str]
    message_id: Optional[str]
    in_reply_to: Optional[str]
    references: Optional[str]
    request_type: Optional[str]

    # document
    file_path: Optional[str]
    title: Optional[str]

    chunk_index: int
    total_chunks: int
    extra: Optional[Dict] = None

@dataclass
class Chunk:
    text: str
    metadata: ChunkMetadata
