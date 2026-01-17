#!/usr/bin/env python3
"""
Wrapper Streamable HTTP per il server MCP finanziario
Implementa il protocollo Streamable HTTP come specificato nelle specifiche MCP
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
from contextlib import asynccontextmanager
from sse_starlette.sse import EventSourceResponse

# Importa il server originale MCP
from financial_mcp_server import app as mcp_app

app = FastAPI(title="Financial Analysis MCP Server - Streamable HTTP Wrapper", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Financial Analysis MCP Server - Streamable HTTP Wrapper", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "financial-mcp-server"}


@app.post("/")
async def handle_mcp_request(request: Request):
    """
    Endpoint principale per le richieste MCP secondo il protocollo Streamable HTTP.
    Riceve richieste POST e le elabora usando il server MCP originale.
    """
    try:
        # Legge il corpo della richiesta
        body = await request.json()
        
        # Determina il tipo di richiesta MCP
        method = body.get("method")
        
        if method == "tools/list":
            # Richiesta per la lista degli strumenti
            tools = await mcp_app.list_tools()
            response_data = {
                "result": [tool.dict() for tool in tools],
                "jsonrpc": "2.0",
                "id": body.get("id")
            }
        elif method == "resources/list":
            # Richiesta per la lista delle risorse
            resources = await mcp_app.list_resources()
            response_data = {
                "result": [resource.dict() for resource in resources],
                "jsonrpc": "2.0",
                "id": body.get("id")
            }
        elif method == "tools/call":
            # Richiesta per chiamare uno strumento
            tool_call_params = body.get("params", {})
            tool_name = tool_call_params.get("name")
            arguments = tool_call_params.get("arguments", {})
            
            if not tool_name:
                raise HTTPException(status_code=400, detail="Tool name is required")
            
            # Chiama lo strumento
            result = await mcp_app.call_tool(tool_name, arguments)
            response_data = {
                "result": result,
                "jsonrpc": "2.0",
                "id": body.get("id")
            }
        elif method == "resources/read":
            # Richiesta per leggere una risorsa
            resource_params = body.get("params", {})
            uri = resource_params.get("uri")
            
            if not uri:
                raise HTTPException(status_code=400, detail="Resource URI is required")
            
            # Legge la risorsa
            result = await mcp_app.read_resource(uri)
            response_data = {
                "result": result,
                "jsonrpc": "2.0",
                "id": body.get("id")
            }
        else:
            # Metodo non supportato
            response_data = {
                "error": {
                    "code": -32601,
                    "message": f"Method {method} not supported"
                },
                "jsonrpc": "2.0",
                "id": body.get("id")
            }
        
        return response_data
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing MCP request: {str(e)}")


@app.get("/stream")
async def mcp_stream(request: Request):
    """
    Endpoint SSE per lo streaming MCP secondo il protocollo Streamable HTTP.
    Permette connessioni persistenti per lo scambio di messaggi MCP.
    """
    async def event_generator():
        try:
            # Invia messaggio di inizializzazione
            yield {
                "event": "init",
                "data": json.dumps({
                    "capabilities": mcp_app.create_initialization_options(),
                    "server_info": {
                        "name": "financial-analysis-server",
                        "version": "1.0.0"
                    }
                })
            }
            
            # Simula la gestione di richieste in streaming
            # In una implementazione completa, qui gestiremmo lo streaming bidirezionale
            while True:
                # Aspetta eventuali eventi dal server MCP
                # Per ora, invia heartbeat periodici
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({
                        "timestamp": asyncio.get_event_loop().time(),
                        "status": "alive"
                    })
                }
                
                # Attendi prima del prossimo messaggio
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            # La connessione è stata chiusa dal client
            yield {
                "event": "close",
                "data": json.dumps({"message": "Connection closed"})
            }
            return

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)