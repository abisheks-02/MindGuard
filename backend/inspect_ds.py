from datasets import load_dataset
try:
    ds = load_dataset('vishnu-n/Tanglish-Corpus-185k', split='train')
    print("Columns:", ds.column_names)
    print("Sample:", ds[0])
except Exception as e:
    print("Error:", e)
