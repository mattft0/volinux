FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y wget \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone and install Volatility 3
RUN git clone https://github.com/volatilityfoundation/volatility3.git /opt/volatility3 \
    && pip install -e /opt/volatility3

# Add Volatility to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/opt/volatility3"

# Copy the application files
COPY backend-dump-analyzer/ .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app", "--workers", "4", "--timeout", "300"]