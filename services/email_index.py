from llama_index.core.node_parser import SentenceSplitter
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class ChunkMetadata:
    source: str
    date: str
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

    def chunk_email(self, text: str, source: str, date: str) -> List[Chunk]:
        raw_chunks = self.splitter.split_text(text)
        total = len(raw_chunks)

        return [
            Chunk(text=c, metadata=ChunkMetadata(source=source, date = date,chunk_index=i, total_chunks=total))
            for i, c in enumerate(raw_chunks)
        ]

  