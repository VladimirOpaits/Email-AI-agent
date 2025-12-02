import chromadb

import logging
import asyncio
import shutil
import os
from typing import List

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from dataclasses import dataclass

@dataclass
class ChunkMetadata:
    source: str
    date: str
    chunk_index: int
    total_chunks: int

@dataclass
class Chunk:
    text: str
    metadata: ChunkMetadata

from config import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBCLient:
    def __init__(self, path: str = "./chromadb_data", collection_name: str = "emails", openai_model: str = "text-embedding-3-small", chunk_size: int = 512, chunk_overlap: int = 50, max_tokens: int = 512, temperature: float = 0.3, max_concurrent_requests: int = 10):
        logger.info(f"Chroma initialized with collection {collection_name}")

        self.client = chromadb.PersistentClient(path = path)
        self.collection_name = collection_name
        self.chroma_collection = self.client.get_or_create_collection(name=collection_name)

        Settings.embed_model = OpenAIEmbedding(model = openai_model, api_key= OPENAI_API_KEY)

        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_vector_store(self.vector_store, storage_context = self.storage_context)

        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    def add_chunks(self, chunks: List[Chunk]):
        nodes = [
            TextNode(
                text = c.text,
                metadata = {"source": c.metadata.source, "date": c.metadata.date, "chunk_index": c.metadata.chunk_index, "total_chunks": c.metadata.total_chunks}
            )
            for c in chunks
        ]
        for node in nodes:
            self.index.insert(node)

    async def add_chunks_async(self, chunks: List[Chunk]):
        nodes = [
            TextNode(
                text = c.text,
                metadata = {"source": c.metadata.source, "chunk_index": c.metadata.chunk_index, "total_chunks": c.metadata.total_chunks}
            )
            for c in chunks
        ]
        async with self.semaphore:
            for node in nodes:
                await self.index.ainsert(node)

    def preview_db(self, limit: int = 10):
            try:
                results = self.chroma_collection.get(limit=limit)
            except Exception:
                return

            ids = results.get('ids', [])
            metadatas = results.get('metadatas', [])
            documents = results.get('documents', [])
            
            num_documents = len(documents)
            
            for i in range(num_documents):
                doc = documents[i]
                metadata = metadatas[i]
                
                source = metadata.get('source', 'N/A')
                chunk_index = metadata.get('chunk_index', '?')
                total_chunks = metadata.get('total_chunks', '?')
                
                print(f"[{i+1}/{num_documents}] ID: {ids[i]}")
                print(f"Source: {source} | Chunk: {chunk_index}/{total_chunks}")
                print(f"Text:\n{doc}")
        
    def clear_db(self, index_storage_path: str = "./storage"):
            try:
                self.client.delete_collection(name=self.collection_name)

                if os.path.exists(index_storage_path):
                    shutil.rmtree(index_storage_path)
                
                self.chroma_collection = self.client.get_or_create_collection(name=self.collection_name)
                self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

                self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
                self.index = VectorStoreIndex.from_vector_store(self.vector_store, storage_context = self.storage_context)
            except Exception as e:
                raise

    def latest_date(self) -> str:
        try:
            results = self.chroma_collection.get(
                limit=100000, 
                include=["metadatas"]
            )
        except Exception:
            return ""

        metadatas = results.get('metadatas', [])
        
        latest_date = ""
        for metadata in metadatas:
            date = metadata.get('date', '')
            if date > latest_date:
                latest_date = date
        
        return latest_date