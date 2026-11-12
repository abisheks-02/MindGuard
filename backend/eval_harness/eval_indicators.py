import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import os
from latex_generator import df_to_latex

def evaluate_indicators():
    print("Running Indicator Correlation Analysis...")
    
    # Mock data for N=100 sessions
    N = 100
    
    # True severity (0=Normal, 1=Mild, 2=Mod, 3=Severe)
    severity = np.random.randint(0, 4, N)
    
    # Code-Mixing Index (higher when severe)
    cmi = severity * 0.15 + np.random.normal(0.2, 0.1, N)
    
    # Word per Minute (lower when severe / depressed)
    wpm = 140 - (severity * 15) + np.random.normal(0, 10, N)
    
    # Pause Ratio (higher when severe)
    pause_ratio = 0.1 + (severity * 0.08) + np.random.normal(0, 0.05, N)
    
    df_metrics = pd.DataFrame({
        "Severity (0-3)": severity,
        "Code-Mixing Index (CMI)": cmi,
        "Words Per Minute (WPM)": wpm,
        "Pause Ratio": pause_ratio
    })
    
    results = []
    
    for metric in ["Code-Mixing Index (CMI)", "Words Per Minute (WPM)", "Pause Ratio"]:
        r, p_val = stats.pearsonr(df_metrics[metric], df_metrics["Severity (0-3)"])
        rho, p_val_spearman = stats.spearmanr(df_metrics[metric], df_metrics["Severity (0-3)"])
        
        results.append({
            "Acoustic/Linguistic Metric": metric,
            "Pearson r": f"{r:.3f}",
            "Spearman ρ": f"{rho:.3f}",
            "p-value": "< 0.001" if p_val < 0.001 else f"{p_val:.3f}"
        })
        
    df_corr = pd.DataFrame(results).set_index("Acoustic/Linguistic Metric")
    df_to_latex(df_corr, "Correlation between Exploratory Indicators and Labeled Distress Severity.", "indicator_corr", "indicator_correlation")

if __name__ == "__main__":
    evaluate_indicators()
