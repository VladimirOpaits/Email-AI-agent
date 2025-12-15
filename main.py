from services.email_ingest import EmailClientFlanker
from services.email_index import EmailIndexer
from services.chroma_db import ChromaDBCLient
from services.query import SmartRetrieverService
from services.email_classifier import EmailClassifierService
from config import OPENAI_API_KEY

from datetime import datetime

def convert_iso_to_imap(iso_date_str: str) -> str:
    dt = datetime.fromisoformat(iso_date_str)
    return dt.strftime('%d-%b-%Y')

email_client = EmailClientFlanker("imap.gmail.com", "emailaicorporation@gmail.com", "uzxg yero fsgj rfws", "INBOX", ssl=True)

email_indexer = EmailIndexer()
email_db = ChromaDBCLient()
email_classifier = EmailClassifierService(OPENAI_API_KEY)

email_db.clear_db()

email_query = SmartRetrieverService(email_db.index, OPENAI_API_KEY)

new_emails = email_client.fetch_new(convert_iso_to_imap("2025-12-01T09:07:20+01:00"))

for email in new_emails:
    classification = email_classifier.classify_email(email)
    email.request_type = classification.category.value
    
    print(f"Classified email {email.message_id} as {email.request_type} because {classification.explanation}")

#print(email_db.latest_date())

#print(email_query.query_emails("Найди мне письмо касательно предмета aspectos legales, и скажи когда надо сдать работу"))





