from sqlalchemy import Column, Integer, Numeric, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base 

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    external_id = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    policies = relationship("Policy", back_populates="client")
    claims = relationship("Claim", back_populates="client_obj")

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(50), unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="ACTIVE")

    client = relationship("Client", back_populates="policies")
    coverages = relationship("PolicyCoverage", back_populates="policy", cascade="all, delete-orphan")
    
    claims = relationship(
        "Claim", 
        back_populates="policy_obj",
        primaryjoin="Policy.policy_number == Claim.policy_id",
        foreign_keys="Claim.policy_id",
        viewonly=True
    )

class PolicyCoverage(Base):
    __tablename__ = "policy_coverages"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    coverage_name = Column(String(100), nullable=False)
    limit_amount = Column(Numeric(15, 2), nullable=False)
    deductible = Column(Numeric(10, 2), default=0.00)

    policy = relationship("Policy", back_populates="coverages")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    
    policy_id = Column(String(50), ForeignKey("policies.policy_number"), index=True, nullable=False)
    
    client_name = Column(String(100), index=True)
    incident_date = Column(DateTime(timezone=True), nullable=True) 
    status = Column(String(20), default="NEW") 
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    source_email_id = Column(String(255), unique=True, nullable=False)
    incident_summary = Column(Text, nullable=True)

    client_obj = relationship("Client", back_populates="claims")
    policy_obj = relationship(
        "Policy", 
        back_populates="claims",
        viewonly=True
    )