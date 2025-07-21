# gemma_api.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from huggingface_hub import login

app = FastAPI()

# --- Debugging: Print Environment Variable ---
hf_token = os.environ.get("HUGGINGFACE_TOKEN")
print(f"DEBUG: HUGGINGFACE_TOKEN detected in Gemma API: {hf_token is not None}")
if hf_token:
    print(f"DEBUG: HUGGINGFACE_TOKEN starts with: {hf_token[:5]}...{hf_token[-5:]}")
else:
    print("DEBUG: HUGGINGFACE_TOKEN is NOT set in Gemma API.")

# --- Explicit Hugging Face Login ---
try:
    if hf_token:
        login(token=hf_token)
        print("DEBUG: Successfully attempted huggingface_hub.login() with provided token in Gemma API.")
    else:
        print("DEBUG: No HUGGINGFACE_TOKEN found for explicit login in Gemma API.")
except Exception as e:
    print(f"DEBUG: Error during huggingface_hub.login() in Gemma API: {e}")

# Global variables for model and tokenizer
gemma_tokenizer = None
gemma_model = None
model_loaded = False

# Load Gemma model (runs once when the service starts)
@app.on_event("startup")
async def load_gemma_model():
    global gemma_tokenizer, gemma_model, model_loaded
    print("DEBUG: Loading Gemma model for API service...")
    try:
        model_id = "google/gemma-2b-it"
        gemma_tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
        gemma_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            token=hf_token
        )
        # Move model to CPU explicitly if not using GPU, ensure it stays
        gemma_model.to("cpu")
        model_loaded = True
        print("DEBUG: Gemma model loaded successfully in API service.")
    except Exception as e:
        print(f"ERROR: Failed to load Gemma model in API service: {e}")
        model_loaded = False
        raise HTTPException(status_code=500, detail=f"Failed to load Gemma model: {e}")

class TextGenerationRequest(BaseModel):
    prompt: str

class TextGenerationResponse(BaseModel):
    generated_text: str

@app.post("/generate_text", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Gemma model not yet loaded.")
    try:
        input_ids = gemma_tokenizer(request.prompt, return_tensors="pt").to(gemma_model.device)
        outputs = gemma_model.generate(
            **input_ids,
            max_new_tokens=100,
            num_beams=1,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        generated_text = gemma_tokenizer.decode(outputs[0], skip_special_tokens=True)
        if generated_text.startswith(request.prompt):
            generated_text = generated_text[len(request.prompt):].strip()
        return {"generated_text": generated_text}
    except Exception as e:
        print(f"ERROR: Text generation failed in Gemma API: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {e}")

# Basic health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model_loaded}