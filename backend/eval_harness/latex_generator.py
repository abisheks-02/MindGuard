import pandas as pd
import os

def df_to_latex(df: pd.DataFrame, caption: str, label: str, filename: str):
    """Converts a pandas DataFrame to a LaTeX table and saves it."""
    latex_code = df.to_latex(
        index=True, 
        escape=False, 
        caption=caption, 
        label=f"tab:{label}",
        column_format="l" + "c" * len(df.columns)
    )
    
    out_dir = "eval_results"
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, f"{filename}.tex"), "w", encoding="utf-8") as f:
        f.write(latex_code)
        
    print(f"Generated {filename}.tex")

def matrix_to_latex(cm, classes, caption: str, label: str, filename: str):
    """Converts a confusion matrix to LaTeX."""
    df = pd.DataFrame(cm, index=classes, columns=classes)
    df.index.name = 'True \ Predicted'
    df_to_latex(df, caption, label, filename)
