# main.py — Cognito | Predictive Axis Group
import os
import logging
import signal
import sys
import re
from datetime import datetime, timezone
from typing import Final
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot_config import BotConfig
from database import initialize_db, get_alert_count
from cogs.threat_intel import ThreatIntel
from cogs.geo_risk import GeoRisk
from cogs.conversation import Conversation
from cogs.voice_alerts import VoiceAlerts
from cogs.market_impact import MarketImpact

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("cognito.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("Cognito")

# ── Config & Env ──────────────────────────────────────────────────────────────
load_dotenv()
config = BotConfig()

DISCORD_TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY")
VIRUSTOTAL_API_KEY: Final[str] = os.getenv("VIRUSTOTAL_API_KEY")
NEWS_API_KEY: Final[str] = os.getenv("NEWS_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

# ── Bot Setup ─────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Cog references (set after load)
threat_intel_cog: ThreatIntel = None
geo_risk_cog: GeoRisk = None
conversation_cog: Conversation = None
voice_cog: VoiceAlerts = None
market_impact_cog: MarketImpact = None

# Channel IDs
ALERT_CHANNEL_ID: int = int(os.getenv("ALERT_CHANNEL_ID", "0"))
VOICE_CHANNEL_ID: int = int(os.getenv("VOICE_CHANNEL_ID", "859570733486571554"))


# ── Graceful Shutdown ─────────────────────────────────────────────────────────
def handle_exit(sig, frame):
    logger.info("Cognito shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

# Initialize database on startup
initialize_db()


# ── Events ────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    global threat_intel_cog, geo_risk_cog, conversation_cog, voice_cog, market_impact_cog

    # Only load cogs on first ready — skip on reconnects
    if threat_intel_cog is not None:
        logger.info("Reconnected to Discord — skipping cog reload.")
        return

    # Load cogs
    voice_cog = VoiceAlerts(bot, VOICE_CHANNEL_ID)
    threat_intel_cog = ThreatIntel(bot)
    geo_risk_cog = GeoRisk(bot)
    conversation_cog = Conversation(bot, OPENAI_API_KEY)
    market_impact_cog = MarketImpact(bot)

    # Voice is NOT added as a cog — plain class only
    await bot.add_cog(threat_intel_cog)
    await bot.add_cog(geo_risk_cog)
    await bot.add_cog(conversation_cog)
    await bot.add_cog(market_impact_cog)

    # Wire voice into alert cogs
    # threat_intel_cog.voice_cog = voice_cog
    # geo_risk_cog.voice_cog = voice_cog

    # Set alert channel
    if ALERT_CHANNEL_ID:
        threat_intel_cog.alert_channel_id = ALERT_CHANNEL_ID
        geo_risk_cog.alert_channel_id = ALERT_CHANNEL_ID
        logger.info(f"Alert channel set to ID: {ALERT_CHANNEL_ID}")
    else:
        logger.warning("ALERT_CHANNEL_ID not set — automated alerts disabled until configured.")

    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=config.status_message
        )
    )

    # Announce bot is online
    channel = bot.get_channel(ALERT_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🟢 Cognito Online",
            description="Threat intelligence and geopolitical risk monitoring is active.",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="CISA Monitor", value="✅ Active", inline=True)
        embed.add_field(name="CVE Monitor", value="✅ Active", inline=True)
        embed.add_field(name="Geo Monitor", value="✅ Active", inline=True)
        embed.add_field(
            name="How to interact",
            value="Mention @Cognito or use `!help`",
            inline=False
        )
        embed.set_footer(text="Predictive Axis Group")
        await channel.send(embed=embed)

    logger.info(f"✅ {config.name} v{config.version} is online | {bot.user}")
    logger.info(f"   Organization: {config.organization}")
    logger.info(f"   Servers: {len(bot.guilds)}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)
    content = message.content.strip()
    channel = str(message.channel)

    # Private message prefix
    is_private = content.startswith(config.private_prefix)
    if is_private:
        content = content[1:].strip()

    if not content:
        return

    # Only respond if mentioned, using a command, or sending a private message
    bot_mentioned = bot.user in message.mentions
    is_command = content.startswith("!")
    if not bot_mentioned and not is_command and not is_private:
        return

    # Strip mention from content if present
    if bot_mentioned:
        content = re.sub(r'<@!?\d+>', '', content).strip()
        if not content:
            await message.channel.send(
                f"Hello! I'm Cognito, your threat intelligence advisor. Type `!help` to see what I can do."
            )
            return

    logger.info(f"[{channel}] {message.author} ({user_id}): {content[:80]}")

    # ── Intent Detection & Routing ────────────────────────────────────────────
    intent = conversation_cog._detect_intent(content)

    async with message.channel.typing():

        # CVE Lookup
        if intent["type"] == "cve_lookup":
            embed = await threat_intel_cog.lookup_cve(intent["value"])
            if embed:
                if is_private:
                    await message.author.send(embed=embed)
                else:
                    await message.channel.send(embed=embed)
                return

        # IOC Lookup
        if intent["type"] == "ioc_lookup":
            if not VIRUSTOTAL_API_KEY:
                await message.channel.send(
                    "⚠️ VirusTotal API key not configured. Add `VIRUSTOTAL_API_KEY` to your `.env` file."
                )
                return
            embed = await threat_intel_cog.lookup_ioc(intent["value"], VIRUSTOTAL_API_KEY)
            if embed:
                if is_private:
                    await message.author.send(embed=embed)
                else:
                    await message.channel.send(embed=embed)
                return

        # Market Impact (replaces country risk)
        if intent["type"] == "country_risk":
            embed = await market_impact_cog.get_market_impact(
                intent["value"],
                news_api_key=NEWS_API_KEY,
                openai_client=conversation_cog.client,
                system_prompt=config.system_prompt
            )
            if embed:
                if is_private:
                    await message.author.send(embed=embed)
                else:
                    await message.channel.send(embed=embed)
                return
            # Fallback if no profile found
            await message.channel.send(
                f"I don't have a market impact profile for that region yet. "
                f"Try: Russia, China, Iran, North Korea, Ukraine, Israel, Taiwan, "
                f"Lithium Triangle, SE Asia, Red Sea, or Arctic."
            )
            return

        # News Query
        if intent["type"] == "news_query":
            if NEWS_API_KEY:
                topic = re.sub(
                    r'(latest|news|recent|update|what.s happening|about|on|for)',
                    '', content, flags=re.IGNORECASE
                ).strip()
                topic = topic if topic else content
                embed = await geo_risk_cog.fetch_news_summary(topic, NEWS_API_KEY)
                if embed:
                    if is_private:
                        await message.author.send(embed=embed)
                    else:
                        await message.channel.send(embed=embed)
                    return

        # ── Special Commands ──────────────────────────────────────────────────
        lower = content.lower()

        # Voice test (admin only)
        if lower == "!voicetest" and message.author.guild_permissions.administrator:
            if voice_cog:
                await message.channel.send("🔊 Testing voice connection...")
                await voice_cog.speak(
                    "This is a test of the Cognito voice alert system. Predictive Axis Group, online."
                )
            else:
                await message.channel.send("❌ Voice cog not initialized.")
            return

        # Set alert channel (admin only)
        if lower.startswith("!set alerts") and message.author.guild_permissions.administrator:
            threat_intel_cog.alert_channel_id = message.channel.id
            geo_risk_cog.alert_channel_id = message.channel.id
            await message.channel.send(
                f"✅ Alert channel set to **#{message.channel.name}**. "
                f"Cognito will post threat intel and geopolitical alerts here."
            )
            return

        # Clear conversation history
        if lower in ["!clear", "clear history", "reset", "start over"]:
            conversation_cog.clear_history(user_id)
            await message.channel.send("🔄 Conversation history cleared.")
            return

        # Status check
        if lower in ["!status", "status", "ping"]:
            embed = discord.Embed(
                title=f"📡 {config.name} Status",
                color=discord.Color.green(),
                description=f"**{config.organization}**\nVersion {config.version}"
            )
            embed.add_field(
                name="CISA Monitor",
                value="✅ Active" if threat_intel_cog.cisa_monitor.is_running() else "❌ Inactive",
                inline=True
            )
            embed.add_field(
                name="CVE Monitor",
                value="✅ Active" if threat_intel_cog.cve_monitor.is_running() else "❌ Inactive",
                inline=True
            )
            embed.add_field(
                name="Geo Monitor",
                value="✅ Active" if geo_risk_cog.news_monitor.is_running() else "❌ Inactive",
                inline=True
            )
            embed.add_field(
                name="Alert Channel",
                value=f"<#{threat_intel_cog.alert_channel_id}>" if threat_intel_cog.alert_channel_id else "Not set — use `!set alerts`",
                inline=False
            )
            embed.add_field(
                name="VirusTotal",
                value="✅ Configured" if VIRUSTOTAL_API_KEY else "⚠️ Not configured",
                inline=True
            )
            embed.add_field(
                name="NewsAPI",
                value="✅ Configured" if NEWS_API_KEY else "⚠️ Not configured",
                inline=True
            )
            embed.add_field(
                name="CISA Alerts Tracked",
                value=str(get_alert_count("cisa")),
                inline=True
            )
            embed.add_field(
                name="CVE Alerts Tracked",
                value=str(get_alert_count("nvd")),
                inline=True
            )
            embed.set_footer(text="Predictive Axis Group")
            await message.channel.send(embed=embed)
            return

        # Help
        if lower in ["!help", "help", "what can you do"]:
            embed = discord.Embed(
                title=f"🧠 {config.name} — Capabilities",
                color=discord.Color.blue(),
                description="I'm your threat intelligence and geopolitical risk advisor. Here's what I can do:"
            )
            embed.add_field(
                name="🔍 Threat Intelligence",
                value=(
                    "• Ask about any CVE: *'Tell me about CVE-2024-1234'*\n"
                    "• Look up an IOC: *'Check this IP: 1.2.3.4'*\n"
                    "• Automated CISA & CVE alerts in your alert channel"
                ),
                inline=False
            )
            embed.add_field(
                name="🌐 Geopolitical Risk",
                value=(
                    "• Country risk: *'What's the risk level for Iran?'*\n"
                    "• Latest intel: *'Latest news on ransomware'*\n"
                    "• Automated geopolitical alerts in your alert channel"
                ),
                inline=False
            )
            embed.add_field(
                name="💬 General Analysis",
                value="Mention @Cognito and ask anything about cybersecurity, threat actors, geopolitical events, or risk assessment.",
                inline=False
            )
            embed.add_field(
                name="⚙️ Commands",
                value=(
                    "`!status` — System status\n"
                    "`!voicetest` — Test voice TTS (admin)\n"
                    "`!set alerts` — Set this channel for alerts (admin)\n"
                    "`!clear` — Reset conversation history\n"
                    "`?<message>` — Send response as DM"
                ),
                inline=False
            )
            embed.set_footer(text="Predictive Axis Group | Cognito v1.0.0")
            await message.channel.send(embed=embed)
            return

        # ── AI Conversation (fallback) ────────────────────────────────────────
        response = await conversation_cog.get_ai_response(user_id, content)

        if is_private:
            await message.author.send(response)
        else:
            if len(response) > 1900:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)


# ── Entry Point ───────────────────────────────────────────────────────────────
def main():
    bot.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
