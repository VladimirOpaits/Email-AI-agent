from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from services.models import SimpleClassificationResult

from services.models import EmailClassificationResult, EmailCategory, EmailData, ClaimData 

class EmailClassifierService:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(temperature=0.2, model="gpt-4o", api_key=openai_api_key)


        self.structured_classifier = self.llm.with_structured_output(SimpleClassificationResult)

        CLASSIFICATION_PROMPT = ChatPromptTemplate.from_template("""
        You are an expert email classifier. Classify the email into one of the following categories: 
        InsuranceClaim, GeneralInquiry, or ClaimDialogue. Provide a brief explanation.
        
        Email Content: {email_content}
        """)

        self.classification_chain = (
            CLASSIFICATION_PROMPT
            | self.structured_classifier
        )

        self.structured_extractor = self.llm.with_structured_output(ClaimData)

        EXTRACTION_PROMPT = ChatPromptTemplate.from_template("""
        You are a data extraction specialist. The user is submitting a new insurance claim.
        Extract the required details for the new claim record. If any field is missing or unclear, set it to null (None).
        
        Rules:
        1. Extract policy_id, client_name, incident_date (in YYYY-MM-DD format), and incident_description_summary.
        
        Email Content: {email_content}
        """)
        
        self.extraction_chain = (
            EXTRACTION_PROMPT
            | self.structured_extractor
        )

    def classify_email(self, email: EmailData) -> EmailClassificationResult:
        
        if email.in_reply_to != "" or email.references:
            return EmailClassificationResult(
                category=EmailCategory.CLAIM_DIALOGUE, 
                explanation="The message is a reply.",
                extracted_data=None 
            )
        
        email_content = f"Subject: {email.subject}\n\nBody: {email.body}"
        
        simple_result = self.classification_chain.invoke(
            {"email_content": email_content}
        )

        final_result = EmailClassificationResult(
            category=simple_result.category,
            explanation=simple_result.explanation,
            extracted_data=None
        )

        if final_result.category == EmailCategory.INSURANCE_CLAIM:
            extracted_data: ClaimData = self.extraction_chain.invoke(
                {"email_content": email_content}
            )
            final_result.extracted_data = extracted_data
        
        return final_result