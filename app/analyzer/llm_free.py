import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load .env if present (works locally). In Docker, env vars should be passed via --env-file.
load_dotenv()

# We accept either env var name to avoid mistakes
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")

# A known public model id (and commonly used in HF examples)
DEFAULT_MODEL = "ServiceNow-AI/Apriel-1.6-15b-Thinker"


def free_llm_analyze(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    """
    Calls Hugging Face Inference via huggingface_hub InferenceClient.
    Returns generated text or None if it fails (so our app can fallback to KB/heuristics).
    """
    try:
        client = InferenceClient(model=model, token=HF_TOKEN)

        # Chat-style completion (recommended for instruction-following models)
        resp = client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful log analysis assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.2,
        )

        return resp.choices[0].message.content.strip()

    except Exception as e:
        # Do not crash the API: we fallback to KB/heuristics
        print(f"Free LLM error: {e}")
        return None

