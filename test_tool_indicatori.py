#!/usr/bin/env python3
'''
Script per testare il MCP server localmente
Uso: python test_mcp_server.py
'''

import asyncio
import json
from financial_mcp_server import (
    get_cached_data,
    calcola_rsi,
    calcola_momentum,
    calcola_macd,
    analisi_stagionalita,
    analisi_trend,
    get_realtime_quotes
)

async def test_basic_functions():
    print("=" * 80)
    print("🧪 TEST FUNZIONI BASE")
    print("=" * 80)
    
    ticker = "AAPL"
    print(f"\n📊 Testing ticker: {ticker}\n")
    
    # Test scaricamento dati
    print("1️⃣  Test scaricamento dati...")
    df, info = get_cached_data(ticker)
    print(f"   ✅ Scaricati {len(df)} giorni di dati")
    print(f"   ✅ Azienda: {info.get('longName', 'N/A')}")
    
    # Test RSI
    print("\n2️⃣  Test RSI...")
    rsi = calcola_rsi(df)
    print(f"   ✅ RSI: {rsi:.2f}")
    
    # Test Momentum
    print("\n3️⃣  Test Momentum...")
    momentum = calcola_momentum(df, 10)
    print(f"   ✅ Momentum (10gg): {momentum:.2f}%")
    
    # Test MACD
    print("\n4️⃣  Test MACD...")
    macd = calcola_macd(df)
    print(f"   ✅ MACD: {json.dumps(macd, indent=4)}")
    
    # Test Stagionalità
    print("\n5️⃣  Test Stagionalità...")
    stag = analisi_stagionalita(df)
    print(f"   ✅ Mese migliore: {stag['mese_migliore']} ({stag['rendimento_migliore']:.2f}%)")
    
    # Test Trend
    print("\n6️⃣  Test Trend...")
    trend = analisi_trend(df)
    print(f"   ✅ Trend: {trend['trend']}")
    print(f"   ✅ Prezzo: ${trend['prezzo']:.2f}")

    # Test Realtime Quotes
    print("\n7️⃣  Test Realtime Quotes...")
    tickers_to_test = ["AAPL", "MSFT"]
    realtime_quotes = get_realtime_quotes(tickers_to_test)
    for t, data in realtime_quotes.items():
        print(f"   ✅ {t}: Prezzo {data['price']:.2f} @ {data['timestamp']}")
    
    print("\n" + "=" * 80)
    print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_basic_functions())