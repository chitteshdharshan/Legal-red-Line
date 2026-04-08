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

# Run the custom server script
CMD ["python", "server/app.py"]
