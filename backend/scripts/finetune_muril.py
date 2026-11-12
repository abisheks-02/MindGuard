"""
Fine-tunes the Google MuRIL (Multilingual Representation for Indian Languages) model
on a custom Tanglish dataset for mental health severity classification.
"""

import os
import pandas as pd
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForMaskedLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from transformers.trainer_utils import get_last_checkpoint
import os
from sklearn.model_selection import train_test_split
from datasets import load_dataset, Dataset

# Import PEFT for LoRA
from peft import LoraConfig, get_peft_model

def main():
    # 1. Load the dataset from local CSV
    dataset_path = "data/hf_tanglish_185k.csv"
    print(f"Loading local dataset from {dataset_path}...")
    
    df = pd.read_csv(dataset_path)
    # Ensure all text is string type
    df['text'] = df['text'].astype(str)
    
    # 2. Split into train and validation sets
    print("Splitting train into train and validation sets...")
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)
    
    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)
        
    print(f"Train size: {len(train_dataset)}, Val size: {len(val_dataset)}")
    
    # 3. Load MuRIL tokenizer and model
    # Note: MuRIL is a large model (236M params). We use the base cased version.
    model_name = "google/muril-base-cased"
    print(f"Loading tokenizer and model: {model_name}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # We use Masked LM since the dataset has no mental health labels
    model = AutoModelForMaskedLM.from_pretrained(model_name)
    
    # === APPLY LoRA ===
    print("Applying LoRA (Low-Rank Adaptation) to the model...")
    lora_config = LoraConfig(
        r=8,                   # Rank (how many parameters to add)
        lora_alpha=16,         # Scaling factor
        target_modules=["query", "value"],  # Target attention layers in MuRIL
        lora_dropout=0.1,
        bias="none"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    # ==================
    
    # Data collator for MLM (randomly masks 15% of words for the model to guess)
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=True,
        mlm_probability=0.15
    )
    
    # 4. Tokenization function
    # NOTE: You may need to change "text" to the actual column name used in the dataset 
    # (e.g., "Text", "sentence", "comment")
    text_column = "text" if "text" in train_dataset.column_names else train_dataset.column_names[0]
    
    def tokenize_function(examples):
        return tokenizer(examples[text_column], padding="max_length", truncation=True, max_length=128)
        
    print(f"Tokenizing datasets (using column: {text_column})...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_val = val_dataset.map(tokenize_function, batched=True)
    
    # 5. Define Training Arguments
    # Adjusted for the large 185k dataset
    output_dir = "./models/muril_tanglish_185k"
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="steps",  # Fixed: changed from evaluation_strategy for newer transformers
        eval_steps=1000,
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=1,
        weight_decay=0.01,
        save_strategy="steps",
        save_steps=1000,
        load_best_model_at_end=True,
        logging_steps=100,
        fp16=True, 
    )
    
    # 6. Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        data_collator=data_collator,
    )
    
    # 7. Start Fine-Tuning
    last_checkpoint = None
    if os.path.isdir(output_dir):
        last_checkpoint = get_last_checkpoint(output_dir)
        
    if last_checkpoint is not None:
        print(f"Resuming training from checkpoint: {last_checkpoint}")
    else:
        print("Starting fine-tuning from the beginning...")
        
    trainer.train(resume_from_checkpoint=last_checkpoint)
    
    # 8. Save the final model and tokenizer
    print(f"Saving fine-tuned model to {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Fine-tuning complete!")

if __name__ == "__main__":
    main()
