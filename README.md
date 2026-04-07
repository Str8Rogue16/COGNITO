# Cognito
### Threat Intelligence & Geopolitical Market Impact Bot
**By Predictive Axis Group**

---

Cognito is a Discord intelligence bot that monitors global threats in real time and maps geopolitical events directly to defense and tech stock watchlists. Built for traders, security professionals, and analysts who want signal, not noise.

---

## What Cognito Does

**Threat Intelligence**
- Monitors CISA Known Exploited Vulnerabilities (KEV) feed hourly
- Monitors NIST NVD for HIGH and CRITICAL CVEs hourly
- Deduplicates alerts across restarts using SQLite — no repeated alerts
- Manual CVE lookup by ID
- IOC analysis via VirusTotal (IP addresses, file hashes, domains)

**Geopolitical Market Impact**
- Maps 11 global regions to sector impact ratings and stock watchlists
- Pulls live news headlines as event triggers
- Generates AI analyst takes calibrated for retail traders
- Regions covered: Russia, China, Iran, North Korea, Ukraine, Israel, Taiwan, Lithium Triangle, SE Asia Hub, Red Sea/Panama, Arctic/Nordic

**Conversational Intelligence**
- Natural language interface — mention @Cognito and ask anything
- Context-aware conversation history per user
- Powered by OpenAI GPT-4o-mini

**Automated Monitoring**
- Geopolitical news monitoring every 30 minutes
- Alerts posted automatically to a designated Discord channel
- Reconnect-safe — no duplicate alerts or responses on Discord reconnects

---

## Covered Regions & Key Tickers

| Region | Key Tickers |
|---|---|
| Russia | LMT, RTX, NOC, XOM, CVX, MOS, CF |
| China | NVDA, AMD, AVGO, LMT, NOC, PANW |
| Iran | XOM, CVX, OXY, LMT, RTX, PANW |
| North Korea | NOC, LMT, PANW, CRWD, LDOS |
| Ukraine | LMT, RTX, NOC, AVAV, LHX, MOS |
| Israel | LMT, RTX, AVAV, PANW, CRWD, LHX |
| Taiwan | NVDA, AMD, AVGO, LMT, NOC, AMAT |
| Lithium Triangle | ALB, SQM, LTHM, MP, TSLA |
| SE Asia Hub | AVGO, INTC, AMAT, KLAC, TER |
| Red Sea / Panama | ZIM, DAC, FDX, UPS, XOM, HII |
| Arctic / Nordic | NOC, LMT, RKLB, HII, GE |

---

## Project Structure

```
Cognito/
├── main.py                 # Bot entry point and message routing
├── bot_config.py           # Configuration dataclass and AI system prompt
├── database.py             # SQLite deduplication for alerts
├── .env                    # API keys (not committed to git)
├── ecosystem.config.js     # PM2 process manager config
├── requirements.txt        # Python dependencies
└── cogs/
    ├── threat_intel.py     # CISA KEV and NVD CVE monitoring
    ├── geo_risk.py         # Geopolitical news monitoring
    ├── market_impact.py    # Regional market impact profiles
    ├── conversation.py     # Intent detection and OpenAI integration
    └── voice_alerts.py     # TTS voice alerts (in development)
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js (for PM2)
- FFmpeg (for voice, optional)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/cognito.git
cd cognito
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file
```bash
cp .env.template .env
```

Edit `.env` and fill in your keys:
```
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
VIRUSTOTAL_API_KEY=your_virustotal_api_key
NEWS_API_KEY=your_newsapi_key
ALERT_CHANNEL_ID=your_discord_alert_channel_id
VOICE_CHANNEL_ID=your_discord_voice_channel_id
```

### 4. Get your API keys

| Service | URL | Notes |
|---|---|---|
| Discord Bot | https://discord.com/developers/applications | Enable Message Content Intent |
| OpenAI | https://platform.openai.com/api-keys | Key starts with `sk-` |
| VirusTotal | https://www.virustotal.com | Free tier: 500 lookups/day |
| NewsAPI | https://newsapi.org | Free tier: 100 requests/day |

### 5. Invite Cognito to your Discord server
In the Discord Developer Portal:
- OAuth2 → URL Generator
- Scopes: `bot`
- Permissions: Send Messages, Read Message History, View Channels, Connect, Speak, Embed Links
- Copy the URL and open it in your browser

### 6. Start with PM2
```bash
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## Usage

| What you type | What Cognito does |
|---|---|
| `@Cognito russia` | Returns Russia market impact report |
| `@Cognito taiwan` | Returns Taiwan market impact report |
| `@Cognito CVE-2024-1234` | Looks up that CVE from NIST NVD |
| `@Cognito 1.2.3.4` | Checks IP against VirusTotal |
| `@Cognito what is ransomware` | AI conversation response |
| `!status` | Shows system health and alert counts |
| `!help` | Lists all capabilities |
| `!set alerts` | Sets current channel for automated alerts (admin) |
| `!clear` | Resets your conversation history |
| `?<message>` | Cognito replies via DM |

---

## Automated Alerts

Once `!set alerts` is configured in your Discord server, Cognito will automatically post:

- **CISA KEV Alerts** — New known exploited vulnerabilities (hourly)
- **CVE Alerts** — HIGH and CRITICAL severity CVEs from NIST NVD (hourly)
- **Geopolitical News** — Events matching monitored topics (every 30 min)

The SQLite database (`cognito.db`) tracks all seen alerts. Cognito will never re-alert on the same CVE or CISA entry across restarts.

---

## Customization

Edit `bot_config.py` to customize:
- Cognito's personality and system prompt
- CVE severity threshold for alerts
- Monitored countries list
- News topics to monitor
- Alert check intervals

Edit `cogs/market_impact.py` to:
- Add new regions or countries
- Update ticker watchlists
- Adjust sector impact ratings

---

## Requirements

```
discord.py>=2.3.2
python-dotenv>=1.0.0
openai>=1.0.0
requests>=2.31.0
aiohttp>=3.9.0
feedparser>=6.0.10
apscheduler>=3.10.4
gtts>=2.3.0
PyNaCl>=1.5.0
```

---

## Roadmap

- [ ] Nation-state and non-state threat actor profiles
- [ ] Voice alerts (TTS) on CISA/CVE triggers
- [ ] Raspberry Pi deployment guide
- [ ] Web dashboard for alert history
- [ ] Multi-server SaaS deployment
- [ ] Real-time commodity price feeds
- [ ] Financial modeling integration

---

## Disclaimer

Cognito is an intelligence and research tool. Nothing produced by Cognito constitutes financial advice. Always do your own research before making investment decisions.

---

## About Predictive Axis Group

Predictive Axis Group builds commercial intelligence tools for financial modeling, corporate wargaming, and geopolitical risk assessment for private sector clients.

---

## License

MIT License — see LICENSE file for details.
