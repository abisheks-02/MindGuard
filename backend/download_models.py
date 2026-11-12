import os

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def download_models():
    """Download the optional gated Llama model using an environment token."""
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "HF_TOKEN is required. Set it in your shell before downloading gated models."
        )

    print("Downloading Llama-3.2-3B-Instruct...")
    llama_name = "meta-llama/Llama-3.2-3B-Instruct"
    try:
        quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        AutoTokenizer.from_pretrained(llama_name, token=token)
        AutoModelForCausalLM.from_pretrained(
            llama_name,
            quantization_config=quantization_config,
            device_map="auto",
            token=token,
        )
        print("Llama-3 downloaded successfully.")
    except Exception as exc:
        print(f"Failed to download Llama-3: {exc}")


if __name__ == "__main__":
    download_models()
