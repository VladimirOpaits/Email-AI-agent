from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, List, Optional
from .base import Base 
from .db_models import Claim, Client, Policy, PolicyCoverage

class PostgresRepository:
    def __init__(self, dsn: str):
        self.engine = create_engine(dsn)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine) 

    def get_db_session(self) -> Generator[Session, None, None]:
        db: Session = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # --- Client Methods ---

    def create_client(self, db: Session, **kwargs) -> Client:
        new_client = Client(**kwargs)
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        return new_client

    def get_client_by_id(self, db: Session, client_id: int) -> Optional[Client]:
        return db.get(Client, client_id)

    def get_client_by_email(self, db: Session, email: str) -> Optional[Client]:
        stmt = select(Client).where(Client.email == email)
        return db.scalars(stmt).first()

    # --- Policy Methods ---

    def create_policy(self, db: Session, **kwargs) -> Policy:
        new_policy = Policy(**kwargs)
        db.add(new_policy)
        db.commit()
        db.refresh(new_policy)
        return new_policy

    def get_policy_by_number(self, db: Session, policy_number: str) -> Optional[Policy]:
        stmt = select(Policy).where(Policy.policy_number == policy_number)
        return db.scalars(stmt).first()

    # --- Coverage Methods ---

    def create_coverage(self, db: Session, **kwargs) -> PolicyCoverage:
        new_coverage = PolicyCoverage(**kwargs)
        db.add(new_coverage)
        db.commit()
        db.refresh(new_coverage)
        return new_coverage

    # --- Claim Methods ---

    def create_claim(self, db: Session, **kwargs) -> Claim:
        new_claim = Claim(**kwargs)
        db.add(new_claim)
        db.commit()
        db.refresh(new_claim)
        return new_claim

    def get_claim_by_id(self, db: Session, claim_id: int) -> Optional[Claim]:
        return db.get(Claim, claim_id)

    def get_claim_by_email_id(self, db: Session, email_id: str) -> Optional[Claim]:
        stmt = select(Claim).where(Claim.source_email_id == email_id)
        return db.scalars(stmt).first()

    def get_all_claims(self, db: Session, skip: int = 0, limit: int = 100) -> List[Claim]:
        stmt = select(Claim).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def update_claim(self, db: Session, claim_id: int, **kwargs) -> Optional[Claim]:
        if not kwargs:
            return self.get_claim_by_id(db, claim_id)
        
        stmt = update(Claim).where(Claim.id == claim_id).values(**kwargs)
        db.execute(stmt)
        db.commit()
        return self.get_claim_by_id(db, claim_id)

    def delete_claim(self, db: Session, claim_id: int) -> None:
        stmt = delete(Claim).where(Claim.id == claim_id)
        db.execute(stmt)
        db.commit()