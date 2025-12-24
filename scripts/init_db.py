import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_URL 
from core.db_management.db_repo import PostgresRepository

def init():
    repo = PostgresRepository(DATABASE_URL)

    repo.create_tables()
    print("Tables created successfully.")

    db_gen = repo.get_db_session()
    db = next(db_gen)
    
    try:
        existing_client = repo.get_client_by_email(db, "julian@example.com")
        
        if not existing_client:
            client = repo.create_client(
                db, 
                full_name="Julian De Silva", 
                email="julian@example.com"
            )
            
            policy = repo.create_policy(
                db, 
                policy_number="AXA-990011", 
                client_id=client.id,
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=365)
            )
            
            repo.create_coverage(
                db, 
                policy_id=policy.id, 
                coverage_name="Collision", 
                limit_amount=5000
            )
            print("Database seeded with test data.")
        else:
            print("Database already contains test data.")
    finally:
        db.close()

if __name__ == "__main__":
    init()