from typing import List
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.readers.base import SimpleDirectoryReader
from datetime import datetime
from .models import Chunk, ChunkMetadata

class DocumentIndexer:
    def __init__(self, chunk_size=1024, chunk_overlap=50):
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_separator="\n\n",
            secondary_chunking_regex="[^,.;。？！]+[,.;。？！]?"
        )

    def load_and_chunk_documents(self, directory_path: str) -> List[Chunk]:
        reader = SimpleDirectoryReader(input_dir=directory_path)

        documents = reader.load_data() 
        
        all_chunks: List[Chunk] = []

        for doc in documents:
            file_date = datetime.now().isoformat()
            
            raw_chunks = self.splitter.split_text(doc.text)
            total = len(raw_chunks)
            
            file_name = doc.metadata.get('file_name', 'N/A')
            file_path = doc.metadata.get('file_path', directory_path + '/' + file_name)

            for i, c in enumerate(raw_chunks):
                all_chunks.append(
                    Chunk(text=c, metadata=ChunkMetadata(
                        source=file_name, 
                        document_type='document',
                        date=file_date,
                        
                        subject=None,
                        sender=None,
                        to=None,
                        message_id=None,
                        in_reply_to=None,
                        references=None,
                        
                        file_path=file_path,
                        title=file_name,
                        
                        chunk_index=i, 
                        total_chunks=total)
                    )
                )
        return all_chunks