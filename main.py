from services.email_ingest import EmailClientFlanker
from services.email_index import EmailIndexer
from services.chroma_db import ChromaDBCLient
from services.query import SmartRetrieverService
from config import OPENAI_API_KEY

from datetime import datetime

def convert_iso_to_imap(iso_date_str: str) -> str:
    dt = datetime.fromisoformat(iso_date_str)
    return dt.strftime('%d-%b-%Y')

email_client = EmailClientFlanker("post.uv.es", "vlao@alumni.uv.es", password="dexnagib663", ssl=True)
email_indexer = EmailIndexer()
email_db = ChromaDBCLient()

email_db.clear_db()

email_query = SmartRetrieverService(email_db.index, OPENAI_API_KEY)

new_emails = email_client.fetch_new(convert_iso_to_imap("2025-12-01T09:07:20+01:00"))

for email in new_emails:
    print(f"New email fetched: {email['id']} dated {email['date']}")



#print(email_db.latest_date())

#print(email_query.query_emails("Найди мне письмо касательно предмета aspectos legales, и скажи когда надо сдать работу"))





#email_client = EmailClientFlanker("imap.gmail.com", "663vova@gmail.com", "peqi sguc whxg kohh", "INBOX", ssl=True)