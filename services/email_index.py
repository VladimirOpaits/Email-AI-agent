from llama_index.core.node_parser import SentenceSplitter
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class EmailData:
    id: str
    date: str
    body: str
    subject: str
    from_address: str
    to_addresses: str
    message_id: str
    in_reply_to: str
    references: str
    attachments: List[Dict[str, Any]]
    
@dataclass
class ChunkMetadata:
    source: str
    document_type: str
    date: str
    
    subject: Optional[str]
    sender: Optional[str]
    to: Optional[str]
    message_id: Optional[str]
    in_reply_to: Optional[str]
    references: Optional[str]

    file_path: Optional[str]
    title: Optional[str]

    chunk_index: int
    total_chunks: int
    extra: Optional[Dict] = None

@dataclass
class Chunk:
    text: str
    metadata: ChunkMetadata

class EmailIndexer:
    def __init__(self, chunk_size=2000, chunk_overlap=50):
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_separator="\n\n",
            secondary_chunking_regex="[^,.;。？！]+[,.;。？！]?"
        )

    def chunk_email(self, email_object: EmailData) -> List[Chunk]:
        raw_chunks = self.splitter.split_text(email_object.body)
        total = len(raw_chunks)

        return [
            Chunk(text=c, metadata=ChunkMetadata(
                source=email_object.id, 
                document_type='email',
                date=email_object.date,
                
                subject=email_object.subject,
                sender=email_object.from_address,
                to=email_object.to_addresses,
                message_id=email_object.message_id,
                in_reply_to=email_object.in_reply_to,
                references=email_object.references,
                
                file_path=None,
                title=None,
                
                chunk_index=i, 
                total_chunks=total)
            )
            for i, c in enumerate(raw_chunks)
        ]