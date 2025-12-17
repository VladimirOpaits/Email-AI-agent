from typing import Dict, List, Optional, Any, Union
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

def _format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

class SmartRetrieverService:
    def __init__(self, index: VectorStoreIndex, openai_api_key: str): 
        self.index = index
        self.llm = ChatOpenAI(temperature=0.1, model="gpt-4o", api_key=openai_api_key)

        self.lc_retriever = RunnableLambda(self._retrieve_and_convert)
        
        RAG_PROMPT = ChatPromptTemplate.from_template("""
        You are a helpful assistant specialized in analyzing email communication.
        Answer the question based only on the following context.
        If the context does not contain the answer, state that you cannot find the relevant information.

        Context: {context}
        Question: {question}
        """)

        self.qa_chain = (
            RunnablePassthrough.assign(
                source_documents=self.lc_retriever, 
                context=lambda x: _format_docs(x['source_documents']),
                question=RunnablePassthrough(), 
            )
            | RAG_PROMPT
            | self.llm
            | StrOutputParser()
            | RunnablePassthrough.assign(
                answer=RunnablePassthrough(),
                source_documents=lambda x: x['source_documents']
            )
        )

    def _createmetadata_filters(self, filters_dict: Dict[str, Any]) -> Optional[MetadataFilters]:
        filters: List[ExactMatchFilter] = []
        
        for key, value in filters_dict.items():
             if value is not None and value != "":
                 filters.append(ExactMatchFilter(key=key, value=value))

        return MetadataFilters(filters=filters) if filters else None
        
    def _retrieve_and_convert(self, input_dict: dict) -> List[Document]:
            query_text = input_dict["question"] 

            metadata_filters = self._createmetadata_filters(input_dict.get("filters", {}))
            
            llama_retriever = self.index.as_retriever(filters = metadata_filters) 
            
            nodes: List[NodeWithScore] = llama_retriever.retrieve(query_text)

            return [
                Document(
                    page_content=n.text, 
                    metadata=n.metadata
                ) 
                for n in nodes
            ]

    def query_emails(self, query_text: str, sender: Optional[str] = None, subject: Optional[str] = None) -> Dict:
            
            filter_dict = {
                "sender": sender,
                "subject": subject,
            }

            input_data = {
                "question": query_text,
                "filters": filter_dict,
            }

            result = self.qa_chain.invoke(input_data)
            
            return result