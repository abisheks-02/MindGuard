import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.detection.llm_judge import LLMJudgeDetector
from scripts.evaluate import Evaluator
import time

def evaluate_llm():
    print("Initializing LLM Judge Detector...")
    # Passing None to hf_pipeline triggers the mock fallback.
    # In production, you would pass the actual loaded transformers pipeline here.
    judge = LLMJudgeDetector(hf_pipeline=None)
    
    def detector_wrapper(text):
        # We don't have real translations here, so we pass empty or simple echo
        res = judge.detect(text, translation=text)
        return {"label": res.label, "confidence": res.score}
        
    evaluator = Evaluator(detector_wrapper)
    
    print("Evaluating on 'dev' split...")
    start = time.time()
    
    # We use dev split because the prompt tuning (rubrics) was done on it.
    metrics = evaluator.evaluate(csv_path="data/test_cases.csv", split="dev", output_dir="eval_results")
    
    latency = time.time() - start
    
    print(f"Evaluation complete in {latency:.2f}s.")
    print(f"Macro F1: {metrics['macro_f1']:.3f}")
    print(f"Severe Recall: {metrics['severe_recall']:.3f}")
    print("Results saved to eval_results/cm_dev.png")

if __name__ == "__main__":
    evaluate_llm()
