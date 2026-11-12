from datasets import load_dataset
import pandas as pd
import os

def main():
    print("Downloading 'vishnu-n/Tanglish-Corpus-185k' from Hugging Face...")
    dataset = load_dataset("vishnu-n/Tanglish-Corpus-185k", split="train")
    
    print("Converting to Pandas DataFrame...")
    df = dataset.to_pandas()
    
    os.makedirs("data", exist_ok=True)
    output_path = "data/hf_tanglish_185k.csv"
    
    print(f"Saving to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully saved with {len(df)} rows!")

if __name__ == "__main__":
    main()
