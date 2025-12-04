from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

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

    class Config:
        populate_by_name = True

@dataclass
class ChunkMetadata:
    source: str
    document_type: str 
    date: str
    
    #email
    subject: Optional[str]
    sender: Optional[str]
    to: Optional[str]
    message_id: Optional[str]
    in_reply_to: Optional[str]
    references: Optional[str]

    #document
    file_path: Optional[str]
    title: Optional[str]

    chunk_index: int
    total_chunks: int
    extra: Optional[Dict] = None

@dataclass
class Chunk:
    text: str
    metadata: ChunkMetadata