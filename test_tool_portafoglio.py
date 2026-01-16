#!/usr/bin/env python3
"""
Test dei nuovi tools per la gestione del portafoglio
"""

import asyncio
import json
import sys
import os

# Aggiungi il percorso del server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from financial_mcp_server import (
    valuta_portafoglio,
    crea_portafoglio,
    bilancia_portafoglio
)

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

async def test_valuta_portafoglio():
    print_section("TEST 1: VALUTAZIONE PORTAFOGLIO")
    
    # Portafoglio esempio
    portafoglio = {
        "AAPL": 30.0,
        "MSFT": 25.0,
        "GOOGL": 20.0,
        "TSLA": 15.0,
        "BND": 10.0
    }
    
    print("📊 Portafoglio da valutare:")
    for ticker, perc in portafoglio.items():
        print(f"   {ticker}: {perc}%")
    
    print("\n⏳ Analisi in corso...\n")
    
    risultato = valuta_portafoglio(portafoglio)
    
    print("✅ RISULTATI:\n")
    print(f"📈 Asset nel portafoglio: {risultato['asset_count']}")
    
    if "metriche_portafoglio" in risultato:
        metriche = risultato["metriche_portafoglio"]
        print(f"\n💹 METRICHE PORTAFOGLIO:")
        print(f"   Volatilità: {metriche.get('volatilita_portafoglio', 'N/A')}%")
        print(f"   Numero effettivo asset: {metriche.get('numero_effettivo_asset', 'N/A')}")
        print(f"   Score diversificazione: {metriche.get('diversificazione_score', 'N/A')}%")
        print(f"   Correlazione media: {metriche.get('correlazione_media', 'N/A')}")
    
    if risultato.get("raccomandazioni"):
        print(f"\n💡 RACCOMANDAZIONI:")
        for racc in risultato["raccomandazioni"]:
            print(f"   {racc}")
    
    print("\n📋 ANALISI PER ASSET:")
    for ticker, analisi in risultato["analisi_per_asset"].items():
        if "error" not in analisi:
            print(f"\n   {ticker} ({analisi.get('peso_percentuale')}%):")
            print(f"      Prezzo: ${analisi.get('prezzo_corrente')}")
            print(f"      RSI: {analisi.get('rsi')}")
            print(f"      Momentum 30gg: {analisi.get('momentum_30gg')}%")
            print(f"      Volatilità: {analisi.get('volatilita_annua')}%")
            print(f"      Settore: {analisi.get('settore')}")

async def test_crea_portafoglio():
    print_section("TEST 2: CREAZIONE PORTAFOGLIO")
    
    capitale = 10000
    obiettivo = "bilanciato"
    orizzonte = "medio"
    rischio = "moderato"
    
    print(f"💰 Capitale: ${capitale:,.0f}")
    print(f"🎯 Obiettivo: {obiettivo}")
    print(f"📅 Orizzonte: {orizzonte} termine")
    print(f"⚠️  Rischio: {rischio}")
    
    print("\n⏳ Creazione portafoglio...\n")
    
    risultato = crea_portafoglio(capitale, obiettivo, orizzonte, rischio)
    
    print("✅ PORTAFOGLIO SUGGERITO:\n")
    
    print("📊 ALLOCAZIONE PERCENTUALE:")
    for ticker, perc in risultato["allocazione_percentuale"].items():
        print(f"   {ticker}: {perc}%")
    
    print(f"\n💵 ALLOCAZIONE IMPORTI:")
    for ticker, importo in risultato["allocazione_importi"].items():
        print(f"   {ticker}: ${importo:,.2f}")
    
    print(f"\n📈 ANALISI ASSETS:")
    for ticker, analisi in risultato["analisi_assets"].items():
        if "error" not in analisi:
            print(f"\n   {ticker}:")
            print(f"      Prezzo: ${analisi.get('prezzo', 0):.2f}")
            print(f"      Azioni: {analisi.get('shares', 0)}")
            print(f"      Importo: ${analisi.get('importo_effettivo', 0):,.2f}")
            print(f"      Volatilità: {analisi.get('volatilita', 0):.2f}%")
            print(f"      Momentum: {analisi.get('momentum', 0):.2f}%")
    
    print(f"\n💰 Totale investito: ${risultato['totale_investito']:,.2f}")
    print(f"📝 Note: {risultato['note']}")

async def test_bilancia_portafoglio():
    print_section("TEST 3: BILANCIAMENTO PORTAFOGLIO")
    
    # Portafoglio corrente (sbilanciato)
    corrente = {
        "AAPL": 40.0,
        "MSFT": 30.0,
        "GOOGL": 20.0,
        "BND": 10.0
    }
    
    # Target (bilanciato)
    target = {
        "AAPL": 25.0,
        "MSFT": 25.0,
        "GOOGL": 25.0,
        "BND": 25.0
    }
    
    print("📊 PORTAFOGLIO CORRENTE:")
    for ticker, perc in corrente.items():
        print(f"   {ticker}: {perc}%")
    
    print("\n🎯 ALLOCAZIONE TARGET:")
    for ticker, perc in target.items():
        print(f"   {ticker}: {perc}%")
    
    print("\n⏳ Calcolo operazioni necessarie...\n")
    
    risultato = bilancia_portafoglio(corrente, target)
    
    print("✅ OPERAZIONI SUGGERITE:\n")
    
    if risultato["operazioni_suggerite"]:
        for op in risultato["operazioni_suggerite"]:
            emoji = "📈" if op["azione"] == "ACQUISTA" else "📉"
            print(f"   {emoji} {op['azione']:10} {op['ticker']:6} -> {op['percentuale']:+6.2f}% (Priorità: {op['priorita']})")
    else:
        print("   ✅ Nessuna operazione necessaria")
    
    print(f"\n📊 ANALISI:")
    analisi = risultato["analisi"]
    print(f"   Numero operazioni: {analisi['numero_operazioni']}")
    print(f"   Drift totale: {analisi['drift_totale']:.2f}%")
    print(f"   Necessita ribilanciamento: {'Sì' if analisi['necessita_ribilanciamento'] else 'No'}")
    print(f"   Costo stimato commissioni: ${analisi['costo_stimato_commissioni']}")
    print(f"   💡 Consiglio: {analisi['consiglio']}")

async def test_tutti():
    """Esegue tutti i test"""
    print("\n" + "🚀" * 40)
    print("    TEST COMPLETO TOOLS GESTIONE PORTAFOGLIO")
    print("🚀" * 40)
    
    try:
        await test_valuta_portafoglio()
        await test_crea_portafoglio()
        await test_bilancia_portafoglio()
        
        print("\n" + "=" * 80)
        print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n💡 Questo script testa i nuovi tools per la gestione del portafoglio")
    print("   Assicurati che il server sia configurato correttamente\n")
    
    asyncio.run(test_tutti())