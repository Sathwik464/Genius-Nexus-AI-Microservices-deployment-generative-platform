import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
from PIL import Image
import torch
import base64
from io import BytesIO
from huggingface_hub import login

app = FastAPI()

# --- Debugging: Print Environment Variable ---
hf_token = os.environ.get("HUGGINGFACE_TOKEN")
print(f"DEBUG: HUGGINGFACE_TOKEN detected in SD API: {hf_token is not None}")
if hf_token:
    print(f"DEBUG: HUGGINGFACE_TOKEN starts with: {hf_token[:5]}...{hf_token[-5:]}")
else:
    print("DEBUG: HUGGINGFACE_TOKEN is NOT set in SD API.")

# --- Explicit Hugging Face Login ---
try:
    if hf_token:
        login(token=hf_token)
        print("DEBUG: Successfully attempted huggingface_hub.login() with provided token in SD API.")
    else:
        print("DEBUG: No HUGGINGFACE_TOKEN found for explicit login in SD API.")
except Exception as e:
    print(f"DEBUG: Error during huggingface_hub.login() in SD API: {e}")

# Global variables for model
sd_pipe = None
model_loaded = False
MODEL_ID_SD = "runwayml/stable-diffusion-v1-5" # Define the model ID here for clarity

# Load Stable Diffusion model (runs once when the service starts)
@app.on_event("startup")
async def load_stable_diffusion_model():
    global sd_pipe, model_loaded
    print("DEBUG: Loading Stable Diffusion model for API service...")
    try:
        # Determine appropriate torch_dtype based on device availability
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        sd_pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID_SD, torch_dtype=dtype, token=hf_token)
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        sd_pipe.to(device)
        model_loaded = True
        print("DEBUG: Stable Diffusion model loaded successfully in API service.")
    except Exception as e:
        print(f"ERROR: Failed to load Stable Diffusion model in API service: {e}")
        model_loaded = False
        raise HTTPException(status_code=500, detail=f"Failed to load Stable Diffusion model: {e}")

class ImageGenerationRequest(BaseModel):
    prompt: str

class ImageGenerationResponse(BaseModel):
    image_base64: str

@app.post("/generate_image", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Stable Diffusion model not yet loaded.")
    try:
        # --- CHANGES MADE HERE ---
        image = sd_pipe(
            request.prompt,
            height=384,          # Reduced height for faster generation
            width=384,           # Reduced width for faster generation
            num_inference_steps=25, # Reduced inference steps (default is typically 50)
            guidance_scale=7.5   # Common default, can be adjusted
        ).images[0]
        # --- END CHANGES ---

        # Convert PIL Image to base64 string
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return {"image_base64": img_str}
    except Exception as e:
        print(f"ERROR: Image generation failed in SD API: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

# Basic health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model_loaded}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)