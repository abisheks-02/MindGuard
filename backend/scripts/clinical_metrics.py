import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import pandas as pd

def calculate_clinical_metrics(y_true, y_pred, crisis_label="Severe"):
    """
    Calculates clinical-grade metrics focusing specifically on the Crisis class.
    Treats the problem as Binary: Crisis vs Non-Crisis.
    """
    # Convert to binary problem: 1 if Crisis, 0 otherwise
    y_true_binary = [1 if label == crisis_label else 0 for label in y_true]
    y_pred_binary = [1 if label == crisis_label else 0 for label in y_pred]
    
    # Calculate Confusion Matrix
    tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()
    
    # Calculate Metrics
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # Recall
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0          # Negative Predictive Value
    
    print("="*50)
    print(" CLINICAL METRICS REPORT (CRISIS CLASS ONLY) ")
    print("="*50)
    
    print("\n[ CONFUSION MATRIX ]")
    print(f"True Positives (Crisis Caught)      : {tp}")
    print(f"False Negatives (Crisis Missed)     : {fn}   <-- CRITICAL DANGER")
    print(f"False Positives (False Alarms)      : {fp}")
    print(f"True Negatives (Correctly Ignored)  : {tn}")
    
    print("\n[ CORE METRICS ]")
    print(f"Sensitivity (Recall) : {sensitivity*100:.2f}%  (Target: >95%)")
    print(f"Specificity          : {specificity*100:.2f}%  (Target: >80%)")
    print(f"Precision            : {precision*100:.2f}%")
    print(f"Neg. Predictive Value: {npv*100:.2f}%")
    
    print("\n[ DOCTOR'S SUMMARY ]")
    print(f"Out of {tp+fn} actual crisis cases, the AI successfully caught {tp} and missed {fn}.")
    print(f"When the AI alerted a doctor, it was a real crisis {precision*100:.1f}% of the time.")
    print("="*50)


if __name__ == "__main__":
    # --- Example Usage with Dummy Data ---
    # 50 Severe cases, 150 non-severe cases
    
    # Let's pretend our model predicted these:
    # It missed 3 Severe cases (False Negatives)
    # It falsely alarmed on 12 Moderate cases (False Positives)
    
    y_true_mock = ["Severe"]*50 + ["Moderate"]*50 + ["Mild"]*50 + ["Normal"]*50
    
    y_pred_mock = (
        ["Severe"]*47 + ["Moderate"]*3 +   # 3 Severe missed
        ["Severe"]*12 + ["Moderate"]*38 +  # 12 False alarms
        ["Mild"]*50 + 
        ["Normal"]*50
    )
    
    calculate_clinical_metrics(y_true_mock, y_pred_mock, crisis_label="Severe")
