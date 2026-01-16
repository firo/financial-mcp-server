# Financial Analysis MCP Server

Server MCP per analisi tecnica, fondamentale e gestione di portafogli di asset finanziari.

## 🚀 Installazione

### Metodo 1: Installazione locale

```bash
# Clona/crea la directory
mkdir financial-mcp-server
cd financial-mcp-server

# Installa dipendenze
pip install -r requirements.txt

# Testa il server
python test_mcp_server.py
```

### Metodo 2: Docker (Self-hosting)

```bash
# Build e avvia con Docker Compose
docker-compose up -d

# Verifica logs
docker-compose logs -f
```

## 📋 Resources Disponibili

- `financial://ticker/{TICKER}/history` - Dati storici (2 anni)
- `financial://ticker/{TICKER}/info` - Informazioni aziendali
- `financial://ticker/{TICKER}/quote` - Quotazione corrente

## 🛠️ Tools Disponibili

### Indicatori Tecnici
1. **calcola_rsi** - Relative Strength Index
2. **calcola_momentum** - Momentum price change
3. **calcola_macd** - MACD indicator
4. **calcola_bollinger_bands** - Bollinger Bands
5. **calcola_volatilita** - Annualized volatility
6. **analisi_stagionalita** - Seasonal patterns
7. **analisi_trend** - Trend analysis with moving averages
8. **analisi_completa** - Complete analysis
9. **ottieni_quote_ora** - Real-time quotes for a list of tickers

### Gestione Portafoglio
10. **valuta_portafoglio** - Valuta un portafoglio esistente
11. **proponi_portafoglio** - Propone un portafoglio ottimizzato
12. **crea_portafoglio** - Crea una struttura dati formale per rappresentare un portafoglio
13. **bilancia_portafoglio** - Bilancia un portafoglio esistente

## 🧪 Testing

```bash
# Test locale
python test_mcp_server.py

# Test con Claude Desktop
# 1. Configura claude_desktop_config.json
# 2. Riavvia Claude Desktop
# 3. Verifica che il server appaia nella lista MCP
```

## 🔌 Configurazione Claude Desktop

Modifica `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) o
`%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "financial-analysis": {
      "command": "python",
      "args": ["/PERCORSO/COMPLETO/financial_mcp_server.py"]
    }
  }
}
```

## 📊 Esempio di utilizzo con Claude

```
User: "Analizza AAPL e dimmi se è un buon momento per comprare"

Claude userà automaticamente:
1. financial://ticker/AAPL/history [Resource]
2. calcola_rsi(AAPL) [Tool]
3. analisi_stagionalita(AAPL) [Tool]
4. analisi_trend(AAPL) [Tool]
5. Fornirà una raccomandazione basata sui dati
```

## 🌐 Self-hosting per accesso remoto

### Opzione 1: ngrok (più semplice)

```bash
# Installa ngrok
brew install ngrok  # Mac
# oppure scarica da ngrok.com

# Avvia il server
python financial_mcp_server.py

# Esponi con ngrok
ngrok http 3000
```

### Opzione 2: VPS con reverse proxy

```bash
# Su VPS (Ubuntu/Debian)
apt update && apt install nginx python3-pip

# Setup nginx come reverse proxy
# Configura SSL con Let's Encrypt
```

## 📝 License

MIT