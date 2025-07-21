# Use a slim Python 3.10 image as a base
FROM python:3.10-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by some Python packages
# Example: git is useful, but not strictly required if all downloads are via pip/hf_hub
# Consider adding 'libgl1-mesa-glx' for Pillow/image processing on some systems if issues arise
RUN apt-get update && apt-get install -y \
    git \
    # libgl1-mesa-glx # Uncomment if Pillow or other libs cause issues
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Create the directory for generated outputs inside the container
RUN mkdir -p generated_outputs

# Set environment variable for Streamlit to listen on the correct port for Cloud Run
ENV PORT 8080

# Command to run the Streamlit application
# --server.port must be $PORT
# --server.address 0.0.0.0 makes it accessible outside the container
# --server.headless true prevents opening a browser in the container (not needed in Cloud Run)
ENTRYPOINT ["streamlit", "run", "ui/app.py", "--server.port", "8080", "--server.address", "0.0.0.0", "--server.headless", "true"]