#!/usr/bin/env python3
"""
HTTP/SSE Wrapper per il server MCP finanziario
Implementa un bridge tra HTTP e il server MCP originale che comunica tramite STDIO
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import threading
import queue

from fastapi import FastAPI, HTTPException
from sse_starlette.sse import EventSourceResponse
import uvicorn

# Importa il server originale
from financial_mcp_server import get_mcp_app

app = FastAPI(title="Financial Analysis MCP Server - HTTP Wrapper", version="1.0.0")

# Ottieni l'applicazione MCP
mcp_app = get_mcp_app()

@app.get("/")
async def root():
    return {"message": "Financial Analysis MCP Server - HTTP Wrapper", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "financial-mcp-server"}

@app.get("/tools")
async def list_tools():
    """Endpoint per ottenere la lista degli strumenti MCP."""
    try:
        tools = await mcp_app.list_tools()
        return {"tools": [tool.dict() for tool in tools]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")

@app.get("/resources")
async def list_resources():
    """Endpoint per ottenere la lista delle risorse MCP."""
    try:
        resources = await mcp_app.list_resources()
        return {"resources": [resource.dict() for resource in resources]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting resources: {str(e)}")

@app.post("/call-tool")
async def call_tool_endpoint(request: Dict[Any, Any]):
    """Endpoint per chiamare uno strumento MCP."""
    try:
        tool_name = request.get("name")
        arguments = request.get("arguments", {})

        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")

        # Chiama lo strumento
        result = await mcp_app.call_tool(tool_name, arguments)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling tool: {str(e)}")

@app.post("/read-resource")
async def read_resource_endpoint(request: Dict[Any, Any]):
    """Endpoint per leggere una risorsa MCP."""
    try:
        uri = request.get("uri")

        if not uri:
            raise HTTPException(status_code=400, detail="URI is required")

        result = await mcp_app.read_resource(uri)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading resource: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)