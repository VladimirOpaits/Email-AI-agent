from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base 

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    
    policy_id = Column(String(50), index=True, nullable=False)
    client_name = Column(String(100), index=True)
    
    incident_date = Column(DateTime(timezone=True), nullable=True) 
    status = Column(String(20), default="NEW") 
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    source_email_id = Column(String(255), unique=True, nullable=False)
    
    incident_summary = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Claim(id={self.id}, policy_id='{self.policy_id}', status='{self.status}')>"