FROM python:3.11-slim

# Create a non-root user (standard for Hugging Face Spaces & security)
RUN useradd -m -u 1000 user
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and knowledge base
COPY . .

# Set permissions for non-root user
RUN chown -R user:user /app
USER user

# Set default port to 7860 (Hugging Face Spaces default)
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
