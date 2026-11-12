import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

class Evaluator:
    def __init__(self, detector_func):
        """
        detector_func: A callable that takes a string and returns a dict:
        {"label": str, "confidence": float}
        """
        self.detector = detector_func
        self.classes = ["Normal", "Mild", "Moderate", "Severe"]
        
    def evaluate(self, csv_path="data/test_cases.csv", split="test", output_dir="eval_results"):
        df = pd.read_csv(csv_path)
        if split:
            df = df[df["split"] == split]
            
        y_true = df["label"].tolist()
        y_pred = []
        
        for text in df["text"]:
            result = self.detector(text)
            y_pred.append(result.get("label", "Normal"))
            
        # Metrics
        report = classification_report(y_true, y_pred, labels=self.classes, zero_division=0, output_dict=True)
        cm = confusion_matrix(y_true, y_pred, labels=self.classes)
        
        # Save confusion matrix as PNG
        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(6,5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=self.classes, yticklabels=self.classes)
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.title(f"Confusion Matrix ({split} split)")
        plt.savefig(os.path.join(output_dir, f"cm_{split}.png"), bbox_inches="tight")
        
        return {
            "macro_f1": report["macro avg"]["f1-score"],
            "severe_recall": report["Severe"]["recall"],
            "report": report
        }
