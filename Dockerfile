
# Use official Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Copy all project files (notebooks, src, etc.)
COPY . .

# Create non-root user for security
RUN useradd -m appuser \
    && chown -R appuser /app
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Start the API with Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]