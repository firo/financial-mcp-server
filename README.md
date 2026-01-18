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
1. **calcola_rsi** - Calcola l'Indice di Forza Relativa (RSI) per identificare condizioni di ipercomprato/ipervenduto
2. **calcola_momentum** - Misura la variazione di prezzo su un periodo specifico per identificare la forza del movimento
3. **calcola_macd** - Calcola l'indicatore Moving Average Convergence Divergence (MACD) per identificare trend e segnali di acquisto/vendita
4. **calcola_bollinger_bands** - Calcola le bande di Bollinger per analizzare la volatilità e identificare livelli di supporto/resistenza dinamici
5. **calcola_volatilita** - Calcola la volatilità annualizzata per valutare il rischio associato all'asset
6. **analisi_stagionalita** - Analizza i pattern stagionali per identificare periodi storici di performance positiva/negativa
7. **analisi_trend** - Analizza la tendenza corrente utilizzando medie mobili (MA50 e MA200) per determinare la direzione del mercato
8. **analisi_completa** - Fornisce un'analisi completa che combina indicatori tecnici, stagionalità e dati fondamentali
9. **ottieni_quote_ora** - Ottiene le quotazioni in tempo reale per una lista di ticker

### Gestione Portafoglio
10. **valuta_portafoglio** - Valuta un portafoglio esistente analizzando composizione, metriche di rischio e performance
11. **proponi_portafoglio** - Propone un portafoglio ottimizzato in base a capitale disponibile, obiettivo di investimento, orizzonte temporale e tolleranza al rischio
12. **crea_portafoglio** - Crea una struttura dati formale per rappresentare un portafoglio con validazione della composizione
13. **bilancia_portafoglio** - Suggerisce operazioni di ribilanciamento per allineare il portafoglio a una distribuzione target

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

## 🐳 Utilizzo con Docker

### Metodo 1: Build diretto da GitHub
```bash
# Build dell'immagine direttamente dal repository GitHub
docker build -t financial-mcp-server https://github.com/firo/financial-mcp-server.git

# Esecuzione del container
docker run -p 8000:8000 financial-mcp-server
```

### Metodo 2: Docker Compose con contesto remoto
```bash
# Avvio del servizio usando docker-compose
docker compose -f docker-compose.yml up financial-mcp-server
```

### Metodo 3: Clonando il repository localmente
```bash
# Clona il repository
git clone https://github.com/firo/financial-mcp-server.git
cd financial-mcp-server

# Build e avvio
docker build -t financial-mcp-server .
docker run -p 8000:8000 financial-mcp-server
```

### Metodo 4: Docker Compose con build esplicito
```bash
# Build dell'immagine usando docker-compose
docker compose -f docker-compose.yml build financial-mcp-server

# Avvio del servizio
docker compose -f docker-compose.yml up financial-mcp-server
```

### Metodo 5: Per ambiente di sviluppo
```bash
# Avvio in modalità sviluppo con volumi montati
docker compose -f docker-compose.yml up financial-mcp-server-dev
```

### Metodo 6: Con Portainer
Nel caso di Portainer:
- Usa l'opzione "Build from Git repository" e inserisci l'URL: `https://github.com/firo/financial-mcp-server.git`
- Specifica come Dockerfile path: `Dockerfile`
- Successivamente crea un container dall'immagine appena creata

## 🌐 Self-hosting per accesso remoto

### Opzione 1: ngrok (più semplice)

```bash
# Installa ngrok
brew install ngrok  # Mac
# oppure scarica da ngrok.com

# Avvia il server
python financial_mcp_server.py

# Esponi con ngrok
ngrok http 8000
```

### Opzione 2: VPS con reverse proxy

```bash
# Su VPS (Ubuntu/Debian)
apt update && apt install nginx python3-pip

# Setup nginx come reverse proxy
# Configura SSL con Let's Encrypt
```

## 🔄 Aggiornamento automatico del server

Dopo aver fatto modifiche al codice e fatto push su GitHub:

1. Ferma il container attuale: `docker stop <nome_container>`
2. Rimuovi l'immagine vecchia: `docker rmi financial-mcp-server`
3. Ricrea l'immagine: `docker build -t financial-mcp-server .` (se hai il codice locale) oppure usa la versione da GitHub
4. Avvia il nuovo container

## 📡 Connessione da client esterni

Una volta che il server è in esecuzione con Streamable HTTP transport, i client (Claude, LLM Studio, ecc.) possono connettersi usando una configurazione simile a:

```json
{
  "mcpServers": {
    "financial-analysis": {
      "endpoint": {
        "uri": "http://tuoserver:8000",
        "protocol": "streamable-http"
      }
    }
  }
}
```

Oppure se usi un dominio con HTTPS e reverse proxy:

```json
{
  "mcpServers": {
    "financial-analysis": {
      "endpoint": {
        "uri": "https://tuodominio.com",
        "protocol": "streamable-http"
      }
    }
  }
}
```

## 🔄 Aggiornamento automatico del server

Dopo aver fatto modifiche al codice e fatto push su GitHub:

1. Ferma il container attuale: `docker stop <nome_container>`
2. Rimuovi l'immagine vecchia: `docker rmi financial-mcp-server`
3. Ricrea l'immagine: `docker build -t financial-mcp-server .` (se hai il codice locale) oppure usa la versione da GitHub
4. Avvia il nuovo container

Il server ora supporta connessioni multiple grazie al protocollo Streamable HTTP, consentendo a diversi client di connettersi contemporaneamente.

## 📝 License

MIT