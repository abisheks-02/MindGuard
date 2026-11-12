import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import seaborn as sns
import os

def run_comprehensive_evaluation(y_true, y_pred, y_prob_crisis=None, classes=None):
    """
    Evaluates predictions and generates a full clinical report + ROC AUC curve.
    
    y_true: list of true labels
    y_pred: list of predicted labels
    y_prob_crisis: (Optional) list of probabilities for the "Crisis" class for ROC curve
    classes: list of all possible classes in order
    """
    if classes is None:
        classes = ["Normal", "Mild", "Moderate", "Severe", "Crisis"]
        
    print("="*60)
    print(" COMPREHENSIVE CLINICAL EVALUATION ")
    print("="*60)
    
    # 1. Per-Class Metrics (Precision, Recall, F1)
    print("\n[ PER-CLASS METRICS ]")
    print(classification_report(y_true, y_pred, labels=classes, zero_division=0))
    
    # 2. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    cm_path = os.path.join(os.path.dirname(__file__), "confusion_matrix.png")
    plt.savefig(cm_path, bbox_inches="tight")
    print(f"\n[!] Confusion matrix saved to: {cm_path}")
    
    # 3. Crisis-Specific Binary Metrics (Assuming 'Crisis' is the target)
    crisis_label = "Crisis" if "Crisis" in y_true else "Severe"
    print(f"\n[ {crisis_label.upper()} SPECIFIC METRICS ]")
    
    y_true_bin = [1 if y == crisis_label else 0 for y in y_true]
    y_pred_bin = [1 if y == crisis_label else 0 for y in y_pred]
    
    tn, fp, fn, tp = confusion_matrix(y_true_bin, y_pred_bin).ravel()
    
    sensitivity = tp / (tp + fn) if (tp+fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn+fp) > 0 else 0
    precision = tp / (tp + fp) if (tp+fp) > 0 else 0
    
    print(f"Sensitivity (Recall): {sensitivity*100:.1f}% -> Out of all real crises, how many were caught?")
    print(f"Specificity         : {specificity*100:.1f}% -> Out of all safe cases, how many were ignored?")
    print(f"Precision           : {precision*100:.1f}% -> When predicting crisis, how often is it right?")
    
    # 4. ROC-AUC Curve
    if y_prob_crisis is not None:
        fpr, tpr, _ = roc_curve(y_true_bin, y_prob_crisis)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate (1 - Specificity)')
        plt.ylabel('True Positive Rate (Sensitivity)')
        plt.title('Receiver Operating Characteristic (Crisis Detection)')
        plt.legend(loc="lower right")
        roc_path = os.path.join(os.path.dirname(__file__), "roc_curve.png")
        plt.savefig(roc_path, bbox_inches="tight")
        print(f"[!] ROC Curve saved to: {roc_path}")
        print(f"ROC-AUC Score       : {roc_auc:.3f}")

if __name__ == "__main__":
    # --- MOCK DATA FOR DEMONSTRATION ---
    # Imagine 200 cases: 40 of each class
    classes = ["Normal", "Mild", "Moderate", "Severe", "Crisis"]
    
    # Ground Truth
    y_true = []
    for c in classes: y_true.extend([c]*40)
    
    # Predictions (Simulating a good model that catches most Crisis, but false alarms on Severe)
    y_pred = (
        ["Normal"]*38 + ["Mild"]*2 +
        ["Mild"]*35 + ["Normal"]*5 +
        ["Moderate"]*30 + ["Severe"]*10 +
        ["Severe"]*30 + ["Crisis"]*10 + # 10 False Alarms (Severe classified as Crisis)
        ["Crisis"]*38 + ["Severe"]*2    # 2 Missed Crises (Crisis classified as Severe)
    )
    
    # Fake probabilities for ROC curve (closer to 1.0 means more likely Crisis)
    y_prob_crisis = []
    for true, pred in zip(y_true, y_pred):
        if true == "Crisis" and pred == "Crisis": y_prob_crisis.append(np.random.uniform(0.8, 1.0))
        elif true == "Crisis" and pred != "Crisis": y_prob_crisis.append(np.random.uniform(0.3, 0.49))
        elif true != "Crisis" and pred == "Crisis": y_prob_crisis.append(np.random.uniform(0.51, 0.7))
        else: y_prob_crisis.append(np.random.uniform(0.0, 0.3))
        
    run_comprehensive_evaluation(y_true, y_pred, y_prob_crisis=y_prob_crisis, classes=classes)
