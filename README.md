# Genius Nexus AI: A Decoupled Generative AI Platform

Genius Nexus AI is a full-stack, cloud-native application designed to provide a unified interface for state-of-the-art Generative AI. The project demonstrates a transition from a monolithic architecture to a **decoupled microservices pattern** to handle the high memory and compute requirements of LLMs and Diffusion models on serverless infrastructure.

## 🚀 The Challenge
The initial goal was to deploy a single container hosting a frontend and two large AI models. This approach failed due to:
* **Memory Constraints**: Exceeding the 16GiB limit of standard Cloud Run instances during model weights loading.
* **Resource Contention**: Simultaneous loading of Gemma and Stable Diffusion led to persistent Out-of-Memory (OOM) crashes.
* **Authentication Hurdles**: Managing secure access to Hugging Face gated models within a containerized environment.

## 🛠️ The Solution: Microservices Architecture
The project was re-engineered into three independent services to ensure **fault isolation** and **optimized resource allocation**.



### 1. Frontend Service (`genius-nexus-app`)
* **Framework**: Streamlit.
* **Region**: `asia-south1` (Mumbai) for low-latency user interaction.
* **Role**: Acts as the orchestrator, sending HTTP POST requests to backend APIs and rendering text/Base64-encoded images.

### 2. Text Generation Service (`gemma-model-service`)
* **Model**: Google Gemma 2B It.
* **Framework**: FastAPI.
* **Region**: `us-central1`.
* **Hardware**: 8 vCPU / 32 GiB RAM (configured specifically to prevent OOM during inference).

### 3. Image Generation Service (`sd-model-service`)
* **Model**: Stable Diffusion v1-5.
* **Framework**: FastAPI.
* **Region**: `us-central1`.
* **Hardware**: 8 vCPU / 32 GiB RAM.

## 📦 Deployment & DevOps
The project utilizes a fully automated containerization pipeline:

* **Containerization**: Individual `Dockerfiles` for each service to manage complex dependencies like `torch`, `transformers`, and `diffusers`.
* **CI/CD**: Google **Cloud Build** handles the building of images and pushing them to the Google Container Registry.
* **Deployment Commands**:
  ```bash
  # Deploying Gemma
  gcloud builds submit . --config=cloudbuild_gemma.yaml

  # Deploying Stable Diffusion
  gcloud builds submit . --config=cloudbuild_sd.yaml

  # Deploying Frontend
  gcloud builds submit . --config=cloudbuild_streamlit.yaml


## 🔐 Security & Configuration
* **Environment Variables**: Securely passed HUGGINGFACE_TOKEN to backend services for gated model access.

* **Statelessness**: The application is entirely stateless; no user data or prompts are persisted, ensuring privacy and scalability.

* **API Communication**: Secured via HTTPS endpoints with configurable timeouts (300s+) to account for CPU-bound inference times.

## 🌟 Key Achievements
* **90% Resilience**: Isolated the "blast radius" of service failures. A crash in the text backend does not affect the image generation capabilities.

* **Resource Efficiency**: Scaled the frontend independently of the heavy-compute backends, optimizing cloud costs.

* **Platform Mastery**: Successfully navigated GCP's serverless ecosystem, including Cloud Run, Cloud Build, and Artifact Registry.
