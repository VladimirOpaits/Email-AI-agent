from typing import List
from llama_index.core.node_parser import SentenceSplitter

from .models import Chunk, ChunkMetadata, EmailData
from .chroma_db import ChromaDBCLient

class EmailIndexer:
    def __init__(self, chunk_size=2000, chunk_overlap=50):
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_separator="\n\n",
            secondary_chunking_regex="[^,.;。？！]+[,.;。？！]?"
        )

    def index_email(self, email_object: EmailData, db_client: ChromaDBCLient, request_type: str = "general") -> None:
        raw_chunks = self.splitter.split_text(email_object.body)
        total = len(raw_chunks)
        
        chunks_to_add = []
        
        for i, c in enumerate(raw_chunks):
            to_str = ", ".join(email_object.to_addresses) if isinstance(email_object.to_addresses, list) else email_object.to_addresses

            chunk_model = Chunk(text=c, metadata=ChunkMetadata(
                source=email_object.id, 
                document_type='email',
                request_type=request_type,
                date=email_object.date,
                
                subject=email_object.subject,
                sender=email_object.from_address,
                to=to_str,
                message_id=email_object.message_id,
                in_reply_to=email_object.in_reply_to,
                references=email_object.references,
                
                file_path=None,
                title=None,
                
                chunk_index=i, 
                total_chunks=total)
            )
            chunks_to_add.append(chunk_model)

        if chunks_to_add:
             db_client.add_chunks(chunks_to_add)