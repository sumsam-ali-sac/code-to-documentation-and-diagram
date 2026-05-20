# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PDM_CHECK_UPDATE=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install PDM
RUN pip install --no-cache-dir pdm

# Copy dependency files
COPY pyproject.toml pdm.lock ./

# Install dependencies using PDM
RUN pdm install --prod --no-lock --no-editable

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["pdm", "run", "uvicorn", "autodoc.main:app", "--host", "0.0.0.0", "--port", "8000"]
