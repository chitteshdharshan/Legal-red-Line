FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for HF Spaces
EXPOSE 7860

# HF_TOKEN is passed as a secret in HF Spaces — don't hardcode it
ENV HF_TOKEN=""

# Run the OpenEnv server
CMD ["python", "-m", "openenv.cli", "serve", "legal_env:LegalRedLineEnv", "--port", "7860", "--host", "0.0.0.0"]
