FROM python:3.11-slim

WORKDIR /app

# Install build tools + git
RUN apt-get update && \
    apt-get install -y git build-essential gcc python3-dev libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip/setuptools/wheel to latest
RUN python -m pip install --upgrade pip setuptools wheel

# Clone the repository
RUN git clone https://github.com/firo/financial-mcp-server.git ./

# Install requirements (allow pre-releases if some deps are beta)
RUN pip install --pre --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "financial_mcp_server.py"]