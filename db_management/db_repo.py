from unittest import result
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, List, Optional
from .base import Base 
from .db_models import Claim 

class PostgresRepository:
    def __init__(self, dsn: str):
        self.engine = create_engine(dsn)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine) #фабрика

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine) 

    def get_db_session(self) -> Generator[Session, None, None]:
        db: Session = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_claim_by_id(self, db: Session, claim_id: int) -> Optional[Claim]:
        stmt = select(Claim).where(Claim.id == claim_id)
        result = db.scalars(stmt).first()
        return result

    def get_all_claims(self, db: Session, skip: int = 0, limit: int = 100) -> List[Claim]:
        stmt = select(Claim).offset(skip).limit(limit)
        result = db.scalars(stmt).all()
        return result
    
    def get_claim_by_email_id(self, db: Session, email_id: str) -> Optional[Claim]:
        stmt = select(Claim).where(Claim.source_email_id == email_id)
        result = db.scalars(stmt).first()
        return result
    
    def update_claim(self, db: Session, claim_id: int, **kwargs) -> Optional[Claim]:
        if not kwargs:
            return self.get_claim_by_id(db, claim_id)
        
        set_clauses = [f"{key} = :{key}" for key in kwargs.keys()]
        sql_set = ", ".join(set_clauses)

        params = kwargs.copy()
        params['claim_id'] = claim_id

        sql_query = text(
            f"UPDATE claims SET {sql_set} WHERE id = :claim_id"
        ).bindparams(**params)

        db.execute(sql_query)
        db.commit()

        return self.get_claim_by_id(db, claim_id)
    
    def create_claim(self, db: Session, **kwargs) -> Claim:
        columns = ", ".join(kwargs.keys())
        values_placeholders = ", ".join([f":{key}" for key in kwargs.keys()])

        sql_query = text(
            f"INSERT INTO claims ({columns}) VALUES ({values_placeholders}) RETURNING *"
        ).bindparams(**kwargs)

        result = db.scalars(sql_query).first()
        db.commit()
        return result
    
    def delete_claim(self, db: Session, claim_id: int) -> None:
        sql_query = text(
            "DELETE FROM claims WHERE id = :claim_id"
        ).bindparams(claim_id=claim_id)

        db.execute(sql_query)
        db.commit()