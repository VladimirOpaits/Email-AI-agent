import imaplib
from datetime import datetime, timezone
from flanker import mime
import re
from html import unescape
from typing import Optional, List, Dict, Any

from flanker.mime import message

class EmailClientFlanker:
    def __init__(self, host, username, password, mailbox="INBOX", port=993, ssl=True):
        self.host = host
        self.username = username
        self.password = password
        self.mailbox = mailbox
        self.port = port
        self.ssl = ssl
        self.conn = None

    def connect(self):
        if self.ssl:
            self.conn = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            self.conn = imaplib.IMAP4(self.host, self.port)
        self.conn.login(self.username, self.password)
        self.conn.select(self.mailbox)

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn.logout()
            self.conn = None

    def _extract_text_from_html(self, html_content):
        if not html_content:
            return ""
        
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</p>', '\n\n', html_content, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', html_content)
        text = unescape(text)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

    def _get_header(self, parsed, header_name):
        try:
            value = parsed.headers.get(header_name, "")
            return value if value else ""
        except:
            return ""

    def _get_email_body(self, parsed):
        body_text = ""
        body_html = ""

        def extract_body(part):
            nonlocal body_text, body_html
            content_type = str(part.content_type).lower() if part.content_type else ""

            if content_type == "text/plain" and not body_text:
                body_text = part.body or ""
            elif content_type == "text/html" and not body_html:
                body_html = part.body or ""

            if hasattr(part, "parts") and part.parts:
                for subpart in part.parts:
                    extract_body(subpart)

        extract_body(parsed)

        if body_text:
            text = body_text.replace('\r', '')
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        elif body_html:
            return self._extract_text_from_html(body_html)

        return ""

    def _parse_raw_email(self, raw_msg: bytes) -> tuple:
        parsed = mime.from_string(raw_msg)
        date_raw = self._get_header(parsed, "Date")
        date = datetime.now(timezone.utc)

        if date_raw:
            try:
                date = datetime.strptime(date_raw, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                try:
                    date = datetime.strptime(date_raw.split('(')[0].strip(), "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    try:
                        date = datetime.strptime(date_raw[:25].strip(), "%a, %d %b %Y %H:%M:%S")
                        if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
                            date = date.replace(tzinfo=timezone.utc)
                    except:
                        pass
        
        return parsed, date

    def _collect_attachments(self, parsed_mime: mime.message) -> List[Dict[str, Any]]:
        attachments = []
        
        def collect_attachments_recursive(part):
            if part.is_attachment():
                filename = part.filename or ""
                
                attachments.append({
                    "filename": filename,
                    "content_type": str(part.content_type) if part.content_type else "",
                    "size": len(part.body) if part.body else 0
                })
            
            if hasattr(part, "parts") and part.parts:
                for sub in part.parts:
                    collect_attachments_recursive(sub)

        collect_attachments_recursive(parsed_mime)
        return attachments

    def _process_email_data(self, uid: bytes, parsed_mime: mime.message, date: datetime, attachments: List, body: str) -> Dict[str, Any]:
        return {
            "id": uid.decode(),
            "subject": parsed_mime.subject or "",
            "from": self._get_header(parsed_mime, "From"),
            "to": self._get_header(parsed_mime, "To"),
            "date": date.isoformat(),
            "body": body,
            "attachments": attachments
        }

    def fetch_new(self, since_date_imap_format: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        self.connect()
        
        search_criteria = ["ALL"]
        if since_date_imap_format:
            search_criteria = ["SINCE", since_date_imap_format]
            
        status, data = self.conn.search(None, *search_criteria)
        
        if not data[0]:
            self.close()
            return []
            
        ids = data[0].split()
        
        if limit:
            ids = ids[-limit:]
        
        emails = []

        for uid in ids:
            status, msg_data = self.conn.fetch(uid, "(RFC822)")
            raw_msg = msg_data[0][1]
            
            parsed_mime, date = self._parse_raw_email(raw_msg)

            attachments = self._collect_attachments(parsed_mime)
            body = self._get_email_body(parsed_mime)

            emails.append(self._process_email_data(
                uid,
                parsed_mime,
                date,
                attachments,
                body
            ))

        self.close()
        return emails