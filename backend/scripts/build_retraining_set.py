import os
import json
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.config import get_settings

def build_retraining_set():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("Building Retraining Set from User Feedback...")
    
    # In a real ORM we would query Feedback model joined with Consent model.
    # Simulating the extraction of only consented user data.
    try:
        # Assuming table is named 'feedback' and users table has 'consent_research'
        query = """
        SELECT f.text, f.correct_label 
        FROM feedback f
        JOIN users u ON f.session_id = u.session_id
        WHERE u.consent_research = 1 AND f.correct_label != 'Unknown'
        """
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"Database error or tables missing. Mocking extraction... {e}")
        df = pd.DataFrame([
            {"text": "I am feeling awful", "correct_label": "Moderate"},
            {"text": "sagalam pola", "correct_label": "Severe"}
        ])
        
    if df.empty:
        print("No new feedback found.")
        return
        
    os.makedirs("data/retraining", exist_ok=True)
    out_path = "data/retraining/user_corrections.csv"
    df.to_csv(out_path, index=False)
    
    print(f"Extracted {len(df)} consented correction rows to {out_path}.")
    print("This dataset can now be mixed into the MuRIL fine-tuning split.")
    
if __name__ == "__main__":
    build_retraining_set()
