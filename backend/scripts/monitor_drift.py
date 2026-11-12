import os
import sys
import time
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.detection.ensemble import EnsembleDetectionService

def monitor_drift():
    print("Starting Weekly Canary Set Drift Monitor...")
    
    # Load canary dataset (a small, highly verified set to test model degradation)
    canary_path = "data/test_cases.csv"
    if not os.path.exists(canary_path):
        print("Canary set not found.")
        return
        
    df = pd.read_csv(canary_path)
    df = df[df["split"] == "test"].head(100) # subset for fast canary
    
    # Initialize Ensemble (Mocked LLM for speed, or actual in prod)
    detection_svc = EnsembleDetectionService()
    
    total = len(df)
    severe_true = 0
    severe_caught = 0
    disagreements = 0
    
    start_time = time.time()
    
    for _, row in df.iterrows():
        res = detection_svc.analyze(row['text'])
        
        # Check Severe Recall
        if row['label'] == "Severe":
            severe_true += 1
            if res['predicted_class'] == "Severe":
                severe_caught += 1
                
        # Check Agreement Rate (if needs_review triggered, there was a major disagreement or low conf)
        if res['needs_review']:
            disagreements += 1
            
    latency = time.time() - start_time
    severe_recall = severe_caught / max(1, severe_true)
    agreement_rate = 1.0 - (disagreements / total)
    
    print(f"Metrics evaluated on {total} canary samples:")
    print(f"- Severe Recall: {severe_recall:.3f}")
    print(f"- Detector Agreement Rate: {agreement_rate:.3f}")
    
    # Alerts
    if severe_recall < 0.95:
        print("ALERT: Model Drift Detected! Severe Recall dropped below 95%.")
        
    if agreement_rate < 0.70:
        print("ALERT: Ensemble Cohesion Dropping! Detectors disagreeing on >30% of inputs.")
        
    # Log to metrics file
    os.makedirs("logs", exist_ok=True)
    with open("logs/drift_monitor.log", "a") as f:
        log_entry = f"{datetime.now().isoformat()} | Recall: {severe_recall:.3f} | Agreement: {agreement_rate:.3f} | Latency: {latency:.2f}s\n"
        f.write(log_entry)
        
    print("Drift log appended to logs/drift_monitor.log")

if __name__ == "__main__":
    monitor_drift()
