FROM python:3.11-slim

WORKDIR /app

# Install git and pip before cloning the repo
RUN apt-get update && apt-get install -y git python3-pip && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/firo/financial-mcp-server.git ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "financial_mcp_server.py"]
