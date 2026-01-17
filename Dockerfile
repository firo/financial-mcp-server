FROM python:3.12-slim

WORKDIR /app

# Install build tools + git
RUN apt-get update && \
    apt-get install -y git build-essential gcc python3-dev libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip/setuptools/wheel to latest
RUN python -m pip install --upgrade pip setuptools wheel

# Clone the repository
RUN git clone https://github.com/firo/financial-mcp-server.git ./

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Assicura che Python non bufferizzi l'output
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run the Streamable HTTP wrapper
CMD ["python", "-u", "-m", "uvicorn", "mcp_streamable_wrapper:app", "--host", "0.0.0.0", "--port", "8000"]