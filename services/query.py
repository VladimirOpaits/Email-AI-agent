from typing import Dict, List
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

def _format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

class Query:
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
            {
                "context": self.lc_retriever | _format_docs, 
                "question": RunnablePassthrough(),
            }
            | RAG_PROMPT
            | self.llm
            | StrOutputParser()
        )
        
    def _retrieve_and_convert(self, input_dict: dict) -> List[Document]:
            query_text = input_dict["question"] 
            
            llama_retriever = self.index.as_retriever() 
            
            nodes: List[NodeWithScore] = llama_retriever.retrieve(query_text)

            return [
                Document(
                    page_content=n.text, 
                    metadata=n.metadata
                ) 
                for n in nodes
            ]

    def query_emails(self, query_text: str) -> Dict:
            source_documents = self._retrieve_and_convert({"question": query_text})
            
            answer = self.qa_chain.invoke({"question": query_text})
            
            return {
                "answer": answer,
                "source_documents": source_documents,
            }