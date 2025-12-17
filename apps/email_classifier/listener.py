import time
from imap_tools import MailBox
from apps.email_classifier.tasks import process_email_task
from apps.email_classifier.celery_app import celery_app
from core.logger import logger

from config import (
    IMAP_HOST, 
    IMAP_USER, 
    IMAP_PASSWORD, 
    IMAP_MAILBOX
)

def listen_for_emails():
    try:
        with MailBox(IMAP_HOST).login(IMAP_USER, IMAP_PASSWORD, initial_folder=IMAP_MAILBOX) as mailbox:
            logger.info(f"Connected to IMAP server, listening in '{IMAP_MAILBOX}'...")

            while True:
                try:
                    responses = mailbox.idle.wait(timeout=600)

                    if responses:
                        for msg in mailbox.fetch(limit=1, reverse=True):
                            msg_id = msg.headers.get('message-id', [str(msg.uid)])[0]

                            email_payload = {
                                "id": str(msg.uid),
                                "subject": msg.subject or "",
                                "from_address": msg.from_,
                                "to_addresses": list(msg.to) if msg.to else [],
                                "date": msg.date.isoformat() if msg.date else "",
                                "body": msg.text or msg.html or "",
                                "message_id": msg_id, 
                                "in_reply_to": msg.headers.get("in-reply-to", [""])[0],
                                "references": msg.headers.get("references", [""])[0],
                                "attachments": [
                                    {
                                        "filename": att.filename,
                                        "content_type": att.content_type,
                                        "size": att.size
                                    } for att in msg.attachments
                                ]
                            }

                            process_email_task.delay(email_payload)
                            logger.info(f"Task dispatched for email UID: {msg.uid}")
                            
                except Exception as inner_e:
                    logger.error(f"IDLE loop error: {inner_e}")
                    time.sleep(10)
                    break 
                            
    except Exception as fatal_e:
        logger.error(f"Fatal connection error: {fatal_e}")
        time.sleep(20)
        return listen_for_emails()
                    
if __name__ == "__main__":
    listen_for_emails()