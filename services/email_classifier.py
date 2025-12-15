from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from services.models import EmailClassificationResult, EmailCategory, EmailData

class EmailClassifierService:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(temperature=0.2, model="gpt-4o", api_key=openai_api_key)

        self.structured_llm = self.llm.with_structured_output(EmailClassificationResult)

        CLASSIFICATION_PROMPT = ChatPromptTemplate.from_template("""
        You are an expert email classifier. Classify the email into one of the following categories: 
        InsuranceClaim, GeneralInquiry, or ClaimDialogue.

        - InsuranceClaim: Emails that contain information about filing a new insurance claim, including details about the incident, policy number, and claimant information.
        - GeneralInquiry: Emails that involve general questions or requests for information that do not pertain to specific claims.
        Classify the email based on its content. Provide a brief explanation for your classification.

        Email Content: {email_content}
        """)

        self.classification_chain = (
            CLASSIFICATION_PROMPT
            | self.structured_llm
        )

    def classify_email(self, email: EmailData) -> EmailClassificationResult:
        if email.in_reply_to != "" or email.references:
            return EmailClassificationResult(category=EmailCategory.CLAIM_DIALOGUE, explanation="The message is a reply.")
        
        email_content = f"Subject: {email.subject}\n\nBody: {email.body}"
        result: EmailClassificationResult = self.classification_chain.invoke(
            {"email_content": email_content}
        )
        return result