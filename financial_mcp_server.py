#!/usr/bin/env python3
"""
Financial Analysis MCP Server - Versione Completa
Server MCP per analisi tecnica, fondamentale e gestione portafogli
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

CACHE_DURATION = 300
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

app = Server("financial-analysis-server")
_data_cache: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_cached_data(ticker: str, periodo: str = "2y") -> Tuple[pd.DataFrame, dict]:
    """Recupera dati storici con cache."""
    cache_key = f"{ticker}_{periodo}"
    now = datetime.now().timestamp()
    
    if cache_key in _data_cache:
        cached = _data_cache[cache_key]
        if now - cached["timestamp"] < CACHE_DURATION:
            return cached["df"], cached["info"]
    
    asset = yf.Ticker(ticker)
    df = asset.history(period=periodo)
    info = asset.info
    
    if df.empty:
        for suffix in [".MI", ".PA", ".L", ".DE"]:
            try:
                alt_ticker = f"{ticker}{suffix}"
                asset = yf.Ticker(alt_ticker)
                df = asset.history(period=periodo)
                if not df.empty:
                    info = asset.info
                    break
            except:
                continue
    
    _data_cache[cache_key] = {"df": df, "info": info, "timestamp": now}
    return df, info


def parse_ticker_uri(uri: str) -> Tuple[str, str]:
    """Estrae ticker e tipo da URI."""
    parts = uri.replace("financial://ticker/", "").split("/")
    ticker = parts[0].upper() if len(parts) > 0 else ""
    resource_type = parts[1] if len(parts) > 1 else "history"
    return ticker, resource_type


def ottieni_quote_ora(tickers: list[str]) -> dict:
    """
    Restituisce il prezzo di chiusura più recente per ogni ticker.

    Args:
        tickers: lista di ticker (es. ['SPY', 'GLD'])

    Returns:
        dict con la struttura {ticker: {'price': float, 'timestamp': datetime}}
    """
    quotes = {}
    for t in tickers:
        # Scarica l'ultimo periodo (default 1d) e prende l’ultima riga
        data = yf.Ticker(t).history(period="1d")
        if not data.empty:
            price   = float(data['Close'].iloc[-1])
            ts      = data.index[-1].to_pydatetime()
            quotes[t] = {"price": price, "timestamp": ts}
    return quotes

# ============================================================================
# INDICATORI TECNICI
# ============================================================================

def calcola_rsi(df: pd.DataFrame, periodo: int = 14) -> float:
    """Calcola RSI."""
    rsi = ta.rsi(df['Close'], length=periodo)
    return float(rsi.iloc[-1]) if not rsi.empty else 0.0


def calcola_momentum(df: pd.DataFrame, periodo: int = 10) -> float:
    """Calcola momentum."""
    if len(df) < periodo:
        return 0.0
    return float((df['Close'].iloc[-1] - df['Close'].iloc[-periodo]) / df['Close'].iloc[-periodo] * 100)


def calcola_macd(df: pd.DataFrame) -> Dict[str, float]:
    """Calcola MACD."""
    macd = ta.macd(df['Close'])
    if macd is None or macd.empty:
        return {"valore": 0.0, "signal": 0.0, "divergenza": 0.0}
    
    return {
        "valore": float(macd['MACD_12_26_9'].iloc[-1]),
        "signal": float(macd['MACDs_12_26_9'].iloc[-1]),
        "divergenza": float(macd['MACDh_12_26_9'].iloc[-1])
    }


def calcola_bollinger_bands(df: pd.DataFrame, periodo: int = 20) -> Dict[str, float]:
    """Calcola Bollinger Bands."""
    bb = ta.bbands(df['Close'], length=periodo)
    if bb is None or bb.empty:
        return {"posizione_percentuale": 0.0, "superiore": 0.0, "inferiore": 0.0}
    
    prezzo = df['Close'].iloc[-1]
    superiore = bb[f'BBU_{periodo}_2.0_2.0'].iloc[-1]
    inferiore = bb[f'BBL_{periodo}_2.0_2.0'].iloc[-1]
    
    posizione = ((prezzo - inferiore) / (superiore - inferiore)) * 100 if superiore != inferiore else 50.0
    
    return {
        "posizione_percentuale": float(posizione),
        "superiore": float(superiore),
        "inferiore": float(inferiore)
    }


def calcola_volatilita(df: pd.DataFrame, periodo: int = 30) -> float:
    """Calcola volatilità annualizzata."""
    rendimenti = df['Close'].pct_change()
    vol = rendimenti.tail(periodo).std() * np.sqrt(252) * 100
    return float(vol)


def analisi_stagionalita(df: pd.DataFrame) -> Dict[str, Any]:
    """Analizza pattern stagionali."""
    df_copia = df.copy()
    df_copia['Mese'] = df_copia.index.month
    df_copia['Rendimento'] = df_copia['Close'].pct_change() * 100
    
    stagionalita = df_copia.groupby('Mese')['Rendimento'].mean()
    mese_corrente = datetime.now().month
    
    return {
        "mese_migliore": int(stagionalita.idxmax()),
        "rendimento_migliore": float(stagionalita.max()),
        "mese_peggiore": int(stagionalita.idxmin()),
        "rendimento_peggiore": float(stagionalita.min()),
        "mese_corrente": mese_corrente,
        "tendenza_mese_corrente": float(stagionalita.get(mese_corrente, 0)),
        "dati_mensili": {int(k): float(v) for k, v in stagionalita.to_dict().items()}
    }


def analisi_trend(df: pd.DataFrame) -> Dict[str, Any]:
    """Analizza trend con medie mobili."""
    prezzo = df['Close'].iloc[-1]
    ma_50 = df['Close'].rolling(50).mean().iloc[-1]
    ma_200 = df['Close'].rolling(200).mean().iloc[-1]
    
    if prezzo > ma_50 > ma_200:
        trend = "Rialzista Forte"
    elif prezzo > ma_50:
        trend = "Rialzista"
    elif prezzo < ma_50 < ma_200:
        trend = "Ribassista Forte"
    else:
        trend = "Ribassista"
    
    return {
        "trend": trend,
        "prezzo": float(prezzo),
        "ma_50": float(ma_50),
        "ma_200": float(ma_200)
    }

# ============================================================================
# GESTIONE PORTAFOGLIO
# ============================================================================

def valuta_portafoglio(holdings: Dict[str, float]) -> Dict[str, Any]:
    """Valuta portafoglio esistente."""
    risultati = {
        "composizione": holdings,
        "asset_count": len(holdings),
        "analisi_per_asset": {},
        "metriche_portafoglio": {},
        "raccomandazioni": []
    }
    
    total = sum(holdings.values())
    if abs(total - 100.0) > 0.1:
        risultati["warning"] = f"Percentuali sommano a {total}%"
    
    rendimenti_giornalieri = []
    volatilita_assets = {}
    
    for ticker, peso in holdings.items():
        try:
            df, info = get_cached_data(ticker, "1y")
            if df.empty:
                risultati["analisi_per_asset"][ticker] = {"error": "Dati non disponibili"}
                continue
            
            prezzo = float(df['Close'].iloc[-1])
            rsi = calcola_rsi(df)
            momentum = calcola_momentum(df, 30)
            volatilita = calcola_volatilita(df, 60)
            
            rendimenti = df['Close'].pct_change().dropna()
            rendimenti_giornalieri.append(rendimenti)
            volatilita_assets[ticker] = volatilita
            
            risultati["analisi_per_asset"][ticker] = {
                "peso_percentuale": peso,
                "prezzo_corrente": round(prezzo, 2),
                "rsi": round(rsi, 2),
                "momentum_30gg": round(momentum, 2),
                "volatilita_annua": round(volatilita, 2),
                "settore": info.get("sector", "N/A"),
                "tipo": info.get("quoteType", "N/A")
            }
        except Exception as e:
            risultati["analisi_per_asset"][ticker] = {"error": str(e)}
    
    if len(rendimenti_giornalieri) >= 2:
        try:
            df_rendimenti = pd.DataFrame({ticker: rend for ticker, rend in zip(holdings.keys(), rendimenti_giornalieri)})
            correlazione = df_rendimenti.corr()
            
            pesi_array = np.array(list(holdings.values())) / 100
            vol_array = np.array([volatilita_assets.get(t, 0) for t in holdings.keys()])
            volatilita_portafoglio = np.sqrt(np.dot(pesi_array**2, vol_array**2))
            
            herfindahl = sum((p/100)**2 for p in holdings.values())
            n_effettivo = 1 / herfindahl if herfindahl > 0 else 0
            
            mask = np.triu_indices_from(correlazione.values, k=1)
            correlazione_media = correlazione.values[mask].mean()
            
            risultati["metriche_portafoglio"] = {
                "volatilita_portafoglio": round(volatilita_portafoglio, 2),
                "numero_effettivo_asset": round(n_effettivo, 2),
                "diversificazione_score": round((n_effettivo / len(holdings)) * 100, 2),
                "correlazione_media": round(correlazione_media, 3)
            }
            
            if volatilita_portafoglio > 25:
                risultati["raccomandazioni"].append("⚠️ Volatilità alta")
            if (n_effettivo / len(holdings)) * 100 < 60:
                risultati["raccomandazioni"].append("📊 Diversificazione bassa")
            if correlazione_media > 0.7:
                risultati["raccomandazioni"].append("🔗 Alta correlazione")
        except Exception as e:
            risultati["metriche_portafoglio"]["error"] = str(e)
    
    return risultati


def proponi_portafoglio(capitale: float, obiettivo: str = "bilanciato", orizzonte: str = "medio", rischio: str = "moderato") -> Dict[str, Any]:
    """Propone un portafoglio ottimizzato."""
    templates = {
        "conservativo_bilanciato": {"BND": 40, "VTI": 25, "VXUS": 15, "VNQ": 10, "GLD": 10},
        "moderato_bilanciato": {"VTI": 35, "VXUS": 25, "BND": 20, "VNQ": 10, "QQQ": 10},
        "aggressivo_bilanciato": {"QQQ": 30, "VTI": 25, "VXUS": 20, "ARKK": 15, "BND": 10},
        "conservativo_crescita": {"VTI": 35, "BND": 30, "VXUS": 20, "VNQ": 15},
        "moderato_crescita": {"VTI": 40, "QQQ": 25, "VXUS": 20, "VNQ": 15},
        "aggressivo_crescita": {"QQQ": 40, "ARKK": 25, "VTI": 20, "VXUS": 15},
        "conservativo_reddito": {"BND": 45, "VYM": 30, "VNQ": 15, "VTI": 10},
        "moderato_reddito": {"VYM": 35, "BND": 30, "VNQ": 20, "VTI": 15},
        "aggressivo_reddito": {"VYM": 40, "VNQ": 25, "VTI": 20, "BND": 15}
    }

    template_key = f"{rischio}_{obiettivo}"
    allocazione = templates.get(template_key, templates["moderato_bilanciato"])
    importi = {ticker: (perc / 100) * capitale for ticker, perc in allocazione.items()}

    analisi_assets = {}
    for ticker in allocazione.keys():
        try:
            df, info = get_cached_data(ticker, "1y")
            if not df.empty:
                analisi_assets[ticker] = {
                    "prezzo": float(df['Close'].iloc[-1]),
                    "shares": int(importi[ticker] / df['Close'].iloc[-1]),
                    "importo_effettivo": round(importi[ticker], 2),
                    "volatilita": round(calcola_volatilita(df), 2),
                    "momentum": round(calcola_momentum(df, 90), 2)
                }
        except:
            analisi_assets[ticker] = {"error": "Dati non disponibili"}

    return {
        "profilo": {"capitale": capitale, "obiettivo": obiettivo, "orizzonte_temporale": orizzonte, "tolleranza_rischio": rischio},
        "allocazione_percentuale": allocazione,
        "allocazione_importi": importi,
        "analisi_assets": analisi_assets,
        "totale_investito": sum(a.get("importo_effettivo", 0) for a in analisi_assets.values()),
        "note": f"Portafoglio {obiettivo} con profilo {rischio}"
    }


def crea_portafoglio(nome: str, holdings: Dict[str, float], meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Crea una struttura dati formale per rappresentare un portafoglio."""
    if not nome:
        raise ValueError("Il nome del portafoglio è obbligatorio")

    # Validazione holdings
    if not holdings:
        raise ValueError("Il portafoglio deve contenere almeno un asset")

    # Controllo che le percentuali sommino a 100%
    totale_percentuale = sum(holdings.values())
    if abs(totale_percentuale - 100.0) > 0.1:
        raise ValueError(f"Le percentuali degli asset devono sommare a 100%, attuale: {totale_percentuale}%")

    # Struttura dati standardizzata per il portafoglio
    portfolio_structure = {
        "nome": nome,
        "tipo": "portfolio",
        "versione": "1.0",
        "data_creazione": datetime.now().isoformat(),
        "holdings": holdings,  # formato: {ticker: percentuale}
        "meta": meta or {},
        "validazione": {
            "percentuale_totale": totale_percentuale,
            "numero_asset": len(holdings),
            "asset_validi": list(holdings.keys())
        }
    }

    return portfolio_structure


def bilancia_portafoglio(holdings_correnti: Dict[str, float], target_allocation: Optional[Dict[str, float]] = None, metodo: str = "ribilanciamento") -> Dict[str, Any]:
    """Bilancia portafoglio."""
    risultati = {
        "portafoglio_corrente": holdings_correnti,
        "operazioni_suggerite": [],
        "nuova_allocazione": {},
        "analisi": {}
    }
    
    if target_allocation is None:
        n_assets = len(holdings_correnti)
        target_allocation = {ticker: 100.0 / n_assets for ticker in holdings_correnti.keys()}
    
    risultati["target_allocation"] = target_allocation
    
    differenze = {}
    for ticker in set(list(holdings_correnti.keys()) + list(target_allocation.keys())):
        corrente = holdings_correnti.get(ticker, 0)
        target = target_allocation.get(ticker, 0)
        diff = target - corrente
        
        if abs(diff) > 1.0:
            differenze[ticker] = diff
    
    for ticker, diff in sorted(differenze.items(), key=lambda x: abs(x[1]), reverse=True):
        if diff > 0:
            risultati["operazioni_suggerite"].append({
                "ticker": ticker,
                "azione": "ACQUISTA",
                "percentuale": round(diff, 2),
                "priorita": "Alta" if abs(diff) > 10 else "Media" if abs(diff) > 5 else "Bassa"
            })
        else:
            risultati["operazioni_suggerite"].append({
                "ticker": ticker,
                "azione": "VENDI",
                "percentuale": round(abs(diff), 2),
                "priorita": "Alta" if abs(diff) > 10 else "Media" if abs(diff) > 5 else "Bassa"
            })
    
    risultati["nuova_allocazione"] = target_allocation
    
    n_operazioni = len(risultati["operazioni_suggerite"])
    drift_totale = sum(abs(d) for d in differenze.values())
    
    risultati["analisi"] = {
        "numero_operazioni": n_operazioni,
        "drift_totale": round(drift_totale, 2),
        "necessita_ribilanciamento": drift_totale > 10,
        "costo_stimato_commissioni": n_operazioni * 2,
        "consiglio": "Ribilancia ora" if drift_totale > 15 else "Ribilancia tra qualche mese" if drift_totale > 10 else "Non necessario"
    }
    
    return risultati

# ============================================================================
# MCP RESOURCES
# ============================================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """Elenca risorse."""
    return [
        Resource(uri="financial://ticker/{ticker}/history", name="Historical Price Data", description="Dati storici", mimeType="application/json"),
        Resource(uri="financial://ticker/{ticker}/info", name="Company Information", description="Info aziendali", mimeType="application/json"),
        Resource(uri="financial://ticker/{ticker}/quote", name="Current Quote", description="Quotazione corrente", mimeType="application/json")
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Leggi risorsa."""
    ticker, resource_type = parse_ticker_uri(uri)
    if not ticker:
        return json.dumps({"error": "Ticker non valido"})
    
    try:
        df, info = get_cached_data(ticker)
        
        if resource_type == "history":
            return json.dumps({"ticker": ticker, "data": df.tail(100).reset_index().to_dict(orient="records")}, default=str)
        elif resource_type == "info":
            return json.dumps({"ticker": ticker, "nome": info.get("longName", "N/A"), "settore": info.get("sector", "N/A")})
        elif resource_type == "quote":
            return json.dumps({"ticker": ticker, "prezzo": float(df['Close'].iloc[-1]), "volume": int(df['Volume'].iloc[-1])})
    except Exception as e:
        return json.dumps({"error": str(e)})
    
    return json.dumps({"error": "Resource type non supportato"})

# ============================================================================
# MCP TOOLS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Elenca tools."""
    return [
        Tool(name="calcola_rsi", description="Calcola RSI", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}, "periodo": {"type": "number", "default": 14}}, "required": ["ticker"]}),
        Tool(name="calcola_momentum", description="Calcola momentum", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}, "periodo": {"type": "number", "default": 10}}, "required": ["ticker"]}),
        Tool(name="calcola_macd", description="Calcola MACD", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}),
        Tool(name="calcola_bollinger_bands", description="Calcola Bollinger Bands", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}, "periodo": {"type": "number", "default": 20}}, "required": ["ticker"]}),
        Tool(name="calcola_volatilita", description="Calcola volatilità", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}, "periodo": {"type": "number", "default": 30}}, "required": ["ticker"]}),
        Tool(name="analisi_stagionalita", description="Analizza stagionalità", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}),
        Tool(name="analisi_trend", description="Analizza trend", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}),
        Tool(name="analisi_completa", description="Analisi completa", inputSchema={"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}),
        Tool(name="ottieni_quote_ora", description="Restituisce quotazioni in tempo reale per una lista di ticker", inputSchema={"type": "object", "properties": {"tickers": {"type": "array", "items": {"type": "string"}}}, "required": ["tickers"]}),
        Tool(name="valuta_portafoglio", description="Valuta portafoglio", inputSchema={"type": "object", "properties": {"holdings": {"type": "object", "additionalProperties": {"type": "number"}}}, "required": ["holdings"]}),
        Tool(name="proponi_portafoglio", description="Propone un portafoglio ottimizzato", inputSchema={"type": "object", "properties": {"capitale": {"type": "number"}, "obiettivo": {"type": "string", "default": "bilanciato"}, "orizzonte": {"type": "string", "default": "medio"}, "rischio": {"type": "string", "default": "moderato"}}, "required": ["capitale"]}),
        Tool(name="crea_portafoglio", description="Crea una struttura dati formale per rappresentare un portafoglio", inputSchema={"type": "object", "properties": {"nome": {"type": "string"}, "holdings": {"type": "object", "additionalProperties": {"type": "number"}}, "meta": {"type": "object", "additionalProperties": True}}, "required": ["nome", "holdings"]}),
        Tool(name="bilancia_portafoglio", description="Bilancia portafoglio", inputSchema={"type": "object", "properties": {"holdings_correnti": {"type": "object", "additionalProperties": {"type": "number"}}, "target_allocation": {"type": "object", "additionalProperties": {"type": "number"}}}, "required": ["holdings_correnti"]})
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Esegue tool."""
    try:
        if name in ["valuta_portafoglio", "proponi_portafoglio", "bilancia_portafoglio", "ottieni_quote_ora", "crea_portafoglio"]:
            if name == "valuta_portafoglio":
                result = valuta_portafoglio(arguments.get("holdings", {}))
            elif name == "proponi_portafoglio":
                result = proponi_portafoglio(arguments.get("capitale"), arguments.get("obiettivo", "bilanciato"), arguments.get("orizzonte", "medio"), arguments.get("rischio", "moderato"))
            elif name == "bilancia_portafoglio":
                result = bilancia_portafoglio(arguments.get("holdings_correnti", {}), arguments.get("target_allocation"))
            elif name == "ottieni_quote_ora":
                result = ottieni_quote_ora(arguments.get("tickers", []))
            elif name == "crea_portafoglio":
                result = crea_portafoglio(
                    arguments.get("nome", ""),
                    arguments.get("holdings", {}),
                    arguments.get("meta")
                )
        else:
            ticker = arguments.get("ticker", "").upper()
            if not ticker:
                return [TextContent(type="text", text=json.dumps({"error": "Ticker richiesto"}))]
            
            df, info = get_cached_data(ticker)
            if df.empty:
                return [TextContent(type="text", text=json.dumps({"error": f"Dati non disponibili per {ticker}"}))]
            
            if name == "calcola_rsi":
                result = {"ticker": ticker, "rsi": calcola_rsi(df, arguments.get("periodo", 14))}
            elif name == "calcola_momentum":
                result = {"ticker": ticker, "momentum": calcola_momentum(df, arguments.get("periodo", 10))}
            elif name == "calcola_macd":
                result = {"ticker": ticker, **calcola_macd(df)}
            elif name == "calcola_bollinger_bands":
                result = {"ticker": ticker, **calcola_bollinger_bands(df, arguments.get("periodo", 20))}
            elif name == "calcola_volatilita":
                result = {"ticker": ticker, "volatilita": calcola_volatilita(df, arguments.get("periodo", 30))}
            elif name == "analisi_stagionalita":
                result = {"ticker": ticker, **analisi_stagionalita(df)}
            elif name == "analisi_trend":
                result = {"ticker": ticker, **analisi_trend(df)}
            elif name == "analisi_completa":
                result = {
                    "ticker": ticker,
                    "nome_azienda": info.get("longName", ticker),
                    "prezzo_corrente": float(df['Close'].iloc[-1]),
                    "indicatori_tecnici": {
                        "rsi": calcola_rsi(df),
                        "momentum_10gg": calcola_momentum(df, 10),
                        "macd": calcola_macd(df),
                        "bollinger_bands": calcola_bollinger_bands(df),
                        "volatilita": calcola_volatilita(df),
                        "trend": analisi_trend(df)
                    },
                    "stagionalita": analisi_stagionalita(df),
                    "fondamentali": {
                        "pe_ratio": info.get("trailingPE"),
                        "market_cap_mld": info.get("marketCap", 0) / 1e9 if info.get("marketCap") else None,
                        "dividend_yield": info.get("dividendYield"),
                        "beta": info.get("beta")
                    }
                }
            else:
                return [TextContent(type="text", text=json.dumps({"error": f"Tool '{name}' non riconosciuto"}))]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

# ============================================================================
# MAIN
# ============================================================================

# Funzione principale rimossa perché il server verrà eseguito tramite il wrapper HTTP
# Il server originale MCP rimane disponibile per essere usato dal wrapper

def get_mcp_app():
    """Restituisce l'applicazione MCP per essere usata dal wrapper HTTP."""
    return app

if __name__ == "__main__":
    # Avvia il wrapper HTTP invece del server diretto
    import subprocess
    import sys
    subprocess.run([sys.executable, "mcp_http_wrapper.py"])