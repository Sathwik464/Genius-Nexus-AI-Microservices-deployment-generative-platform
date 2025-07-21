# app.py (Frontend)
import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import os

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    layout="wide", # Use wide layout for better screen utilization
    page_title="Genius Nexus AI",
    initial_sidebar_state="expanded" # Keep sidebar expanded by default
)

# --- Custom CSS for Gradient Background and Component Styling ---
st.markdown(
    f"""
    <style>
    /* Main app background with a vibrant gradient */
    .stApp {{
        background-image: linear-gradient(to right top, #2C3E50, #4A69BD, #657D9D, #809BCB, #A7C5EB); /* Dark Blue to Light Blue Gradient */
        background-size: cover;
        background-attachment: fixed;
        color: #ecf0f1; /* Light text for readability */
    }}

    /* Sidebar background with a darker, complementary gradient */
    .st-emotion-cache-vk33gh {{ /* This often targets the sidebar directly */
        background-image: linear-gradient(to bottom, #1B263B, #0F172A); /* Darker blue gradient for sidebar */
        color: #ecf0f1;
        padding: 20px;
    }}

    /* Main content block background - semi-transparent for readability over gradient */
    .st-emotion-cache-fg4pbf, .st-emotion-cache-b3z4jh {{ /* These often target the main content containers */
        background-color: rgba(30, 40, 50, 0.85); /* Slightly transparent dark grey-blue */
        padding: 30px;
        border-radius: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3); /* Subtle shadow */
        margin-bottom: 20px;
    }}
    
    /* Text input and text area backgrounds */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: #2e3b4e; /* Darker input fields */
        color: #ecf0f1;
        border-radius: 8px;
        border: 1px solid #4A69BD;
    }}

    /* Button styling */
    .stButton>button {{
        background-color: #4A69BD; /* Match primary color */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #657D9D; /* Lighter on hover */
        color: white;
    }}

    /* Info/Warning/Error boxes */
    .stAlert {{
        border-radius: 8px;
    }}

    /* Ensure text color consistency for headers */
    h1, h2, h3, h4, h5, h6, .st-emotion-cache-10q20pd, .st-emotion-cache-1gsd410 {{
        color: #ecf0f1; /* Light text for headers */
    }}

    /* Adjust padding for columns */
    .st-emotion-cache-1r6dm7f {{ /* This targets the columns themselves */
        padding-right: 1rem;
        padding-left: 1rem;
    }}

    /* --- CUSTOM CHANGES: HIDE TOP-RIGHT PROFILE/EMAIL ICONS AND CHANGE SIDEBAR BRANDING --- */

    /* Hide the top-right profile and message icons */
    .st-emotion-cache-jbl51m, .st-emotion-cache-1f06o2v {{ /* Target the containers for these icons */
        display: none !important;
    }}

    /* Change "Streamlit" text to "Genius Nexus" in the sidebar header */
    .st-emotion-cache-1k46qnj.e1psw1pm4 {{ /* This class targets the Streamlit text itself */
        visibility: hidden; /* Hide the original "Streamlit" text */
        width: 0px; /* Collapse its space */
        height: 0px; /* Collapse its space */
        overflow: hidden; /* Hide overflow */
        position: relative; /* Allow positioning of new content */
    }}
    .st-emotion-cache-1k46qnj.e1psw1pm4::before {{
        content: "Genius Nexus"; /* Insert your desired text */
        visibility: visible; /* Make the new text visible */
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center; /* Center the text */
        color: #ecf0f1; /* Set color for the new text */
        font-size: 1.5rem; /* Adjust font size if needed */
        font-weight: bold;
    }}

    /* --- END CUSTOM CHANGES --- */
    </style>
    """,
    unsafe_allow_html=True
)
# --- End Custom CSS ---

# --- Configuration for Model Service URLs ---
GEMMA_API_URL = os.environ.get("GEMMA_API_URL")
SD_API_URL = os.environ.get("SD_API_URL")

# --- Page Title ---
st.title("Genius Nexus AI: Text & Image Generation 🚀✨")
st.markdown("---")
st.subheader("Unleash creativity with AI-powered text and image generation.")

# --- Sidebar Content ---
with st.sidebar:
    # No need to put 'Genius Nexus' here explicitly, as CSS handles it now
    st.image("https://www.gstatic.com/devrel-devsite/prod/vc39a973d43b468aa22668875ec80337f90f2095f7000305891ce5c128c78a05e/firebase/images/cloud-run.png", width=150) # Cloud Run Logo
    st.header("About Genius Nexus 💡")
    st.write(
        "This application demonstrates the power of generative AI by integrating "
        "Google's **Gemma 2B It** for advanced text generation "
        "and **Stable Diffusion v1-5** for creative image synthesis."
    )
    st.info("Built with Streamlit and deployed on Google Cloud Run for scalability.")
    st.markdown("---")
    st.subheader("Resources & Models")
    st.markdown(" [Google Cloud Run](https://cloud.google.com/run/docs)")
    st.markdown(" [Gemma 2B It on Hugging Face](https://huggingface.co/google/gemma-2b-it)")
    st.markdown(" [Stable Diffusion v1-5 on Hugging Face](https://huggingface.co/runwayml/stable-diffusion-v1-5)")
    st.markdown("---")
    st.markdown("Developed by: Your Name/Team Name") # Optional: Add your name/team

# --- Debugging API URLs (moved to sidebar or an expander for cleaner main UI) ---
with st.expander("API Configuration Status"):
    if not GEMMA_API_URL:
        st.error("GEMMA_API_URL environment variable is NOT set. Text generation will likely fail.")
    else:
        st.success(f"Gemma API URL configured: {GEMMA_API_URL}")
    if not SD_API_URL:
        st.error("SD_API_URL environment variable is NOT set. Image generation will likely fail.")
    else:
        st.success(f"SD API URL configured: {SD_API_URL}")

# --- Main Content Layout with Columns ---
col1, col2 = st.columns(2) # Create two columns for side-by-side sections

# --- Text Generation Section (Left Column) ---
with col1:
    st.header(" Text Generation (Gemma 2B It)")
    st.markdown("Enter your prompt below to generate stories, code, summaries, and more.")
    prompt_text = st.text_area(
        "**Enter your text prompt here:**",
        " ",
        height=150,
        key="gemma_prompt_input" # Unique key for this widget
    )
    
    if st.button("Generate Text", key="gemma_button"):
        if not GEMMA_API_URL:
            st.error("Gemma API URL is not configured. Please ensure it's set as an environment variable during deployment.")
        elif not prompt_text.strip(): # Check if prompt is empty or just whitespace
            st.warning("Please enter a prompt for text generation.")
        else:
            with st.spinner(" Generating text... This might take a moment on CPU infrastructure."):
                try:
                    response = requests.post(f"{GEMMA_API_URL}/generate_text", json={"prompt": prompt_text}, timeout=300) # 5 minutes timeout
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    generated_text = response.json().get("generated_text")
                    if generated_text:
                        st.write("---") # Separator
                        st.subheader("Output:")
                        st.info(generated_text) # Use st.info for a visually distinct output
                    else:
                        st.error("Received empty response or unexpected format from Gemma service.")
                except requests.exceptions.Timeout:
                    st.error(" Request to Gemma service timed out. The model is taking too long to respond. Consider optimizing parameters in the Gemma API (e.g., `max_new_tokens`, `num_beams`).")
                except requests.exceptions.ConnectionError:
                    st.error(" Could not connect to Gemma service. Check if the backend service is running and its URL is correct.")
                except requests.exceptions.RequestException as e:
                    st.error(f" Error calling Gemma service: {e}. Please check the backend service logs for details.")
                except Exception as e:
                    st.error(f" An unexpected error occurred during text generation: {e}")

# --- Image Generation Section (Right Column) ---
with col2:
    st.header(" Image Generation (Stable Diffusion v1-5)")
    st.markdown("Describe the image you want to create below. Be creative!")
    prompt_image = st.text_input(
        "**Enter your image prompt here:**",
        " ",
        key="sd_prompt_input" # Unique key
    )
    
    if st.button("Generate Image", key="sd_button"):
        if not SD_API_URL:
            st.error("Stable Diffusion API URL is not configured. Please ensure it's set as an environment variable during deployment.")
        elif not prompt_image.strip():
            st.warning("Please enter a prompt for image generation.")
        else:
            with st.spinner(" Generating image... This can take some time on CPU."):
                try:
                    response = requests.post(f"{SD_API_URL}/generate_image", json={"prompt": prompt_image}, timeout=300) # 5 minutes timeout
                    response.raise_for_status()
                    image_base64 = response.json().get("image_base64")
                    if image_base64:
                        image_data = base64.b64decode(image_base64)
                        image = Image.open(BytesIO(image_data))
                        st.write("---") # Separator
                        st.subheader("Output:")
                        st.image(image, caption="Generated Image", use_column_width=True)
                    else:
                        st.error("Received empty image data or unexpected format from Stable Diffusion service.")
                except requests.exceptions.Timeout:
                    st.error(" Request to Stable Diffusion service timed out. The model is taking too long to respond. Consider optimizing parameters in the SD API (e.g., `height`, `width`, `num_inference_steps`).")
                except requests.exceptions.ConnectionError:
                    st.error(" Could not connect to Stable Diffusion service. Check if the backend service is running and its URL is correct.")
                except requests.exceptions.RequestException as e:
                    st.error(f" Error calling Stable Diffusion service: {e}. Please check the backend service logs for details.")
                except Exception as e:
                    st.error(f" An unexpected error occurred during image generation: {e}")

# --- Optional: Footer ---
st.markdown("---")
st.markdown("© 2023 Genius Nexus AI. All rights reserved.")






'''# app.py (Frontend)
import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import os

# --- Configuration for Model Service URLs ---
GEMMA_API_URL = os.environ.get("GEMMA_API_URL")
SD_API_URL = os.environ.get("SD_API_URL")

st.set_page_config(layout="wide", page_title="Genius Nexus AI")
st.title("Genius Nexus AI: Text & Image Generation")

# --- Debugging API URLs ---
if not GEMMA_API_URL:
    st.warning("GEMMA_API_URL environment variable is not set. Text generation will not work after deployment.")
if not SD_API_URL:
    st.warning("SD_API_URL environment variable is not set. Image generation will not work after deployment.")

# --- Text Generation Section (Gemma) ---
st.header("Text Generation")
prompt_text = st.text_area("Enter your prompt for text generation:", "")
if st.button("Generate Text"):
    if not GEMMA_API_URL:
        st.error("Gemma API URL is not configured. Please ensure it's set as an environment variable during deployment.")
    else:
        with st.spinner("Generating text..."):
            try:
                response = requests.post(f"{GEMMA_API_URL}/generate_text", json={"prompt": prompt_text}, timeout=300)
                response.raise_for_status()
                generated_text = response.json().get("generated_text")
                if generated_text:
                    st.write("**Generated Text:**")
                    st.write(generated_text)
                else:
                    st.error("Received empty response or unexpected format from Gemma service.")
            except requests.exceptions.Timeout:
                st.error("Request to Gemma service timed out. The model might be taking too long to respond.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to Gemma service. Is the Gemma service deployed and its URL correct?")
            except requests.exceptions.RequestException as e:
                st.error(f"Error calling Gemma service: {e}")
                st.info("Ensure the Gemma model service is deployed and its URL is correct.")
            except Exception as e:
                st.error(f"An unexpected error occurred during text generation: {e}")

st.markdown("---")

# --- Image Generation Section (Stable Diffusion) ---
st.header("Image Generation")
prompt_image = st.text_input("Enter your prompt for image generation:", " ")
if st.button("Generate Image"):
    if not SD_API_URL:
        st.error("Stable Diffusion API URL is not configured. Please ensure it's set as an environment variable during deployment.")
    else:
        with st.spinner("Generating image..."):
            try:
                response = requests.post(f"{SD_API_URL}/generate_image", json={"prompt": prompt_image}, timeout=300)
                response.raise_for_status()
                image_base64 = response.json().get("image_base64")
                if image_base64:
                    image_data = base64.b64decode(image_base64)
                    image = Image.open(BytesIO(image_data))
                    st.image(image, caption="Generated Image", use_column_width=True)
                else:
                    st.error("Received empty image data or unexpected format from Stable Diffusion service.")
            except requests.exceptions.Timeout:
                st.error("Request to Stable Diffusion service timed out. The model might be taking too long to respond.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to Stable Diffusion service. Is the Stable Diffusion service deployed and its URL correct?")
            except requests.exceptions.RequestException as e:
                st.error(f"Error calling Stable Diffusion service: {e}")
                st.info("Ensure the Stable Diffusion model service is deployed and its URL is correct.")
            except Exception as e:
                st.error(f"An unexpected error occurred during image generation: {e}")'''