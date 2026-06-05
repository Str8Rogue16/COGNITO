# bot_config.py — Cognito | Predictive Axis Group
from dataclasses import dataclass, field
from typing import List


@dataclass
class BotConfig:
    # Identity
    name: str = "Cognito"
    version: str = "1.1.0"
    organization: str = "Predictive Axis Group"

    # Behavior
    private_prefix: str = "?"         # ? prefix = DM response
    status_message: str = "Monitoring global threat landscape..."

    # Personality system prompt for OpenAI
    system_prompt: str = (
        "You are Cognito, an intelligence advisor for Predictive Axis Group. "
        "Your role is to provide clear, authoritative analysis on cybersecurity threats, "
        "geopolitical risk, military capability, and emerging global events. "
        "You communicate like a trusted senior analyst — confident, precise, and context-rich. "
        "You never speculate without flagging it. You cite sources when available. "
        "You avoid jargon unless the user clearly understands it. "
        "Keep responses concise but complete. Lead with the most important information. "
        "When asked about threats, always include: severity, affected parties, and recommended action. "
        "When asked about geopolitical events, always include: key actors, potential impact, and timeline. "
        "When asked about military programs or capability, apply the threat vector taxonomy: "
        "Strategic Strike, Cyber Warfare, Electronic Warfare, Autonomous Warfare, "
        "Missile Defense, Force Projection, A2AD, Urban Combat, Cognitive Warfare, Space/PNT Disruption. "
        "Distinguish confirmed capability from assessed or alleged capability. "
        "Flag when information may be outdated. "
        "End responses with a confidence level when appropriate: "
        "[HIGH CONFIDENCE], [MEDIUM CONFIDENCE], or [LOW CONFIDENCE — limited sources]."
    )

    # Feed monitoring intervals (seconds)
    cisa_interval: int = 3600          # Every 1 hour
    cve_interval: int = 3600           # Every 1 hour
    news_interval: int = 1800          # Every 30 minutes

    # CVE severity threshold for alerts (CRITICAL, HIGH, MEDIUM, LOW)
    cve_alert_threshold: str = "HIGH"

    # Countries to monitor for geopolitical risk (ISO codes)
    monitored_countries: List[str] = field(default_factory=lambda: [
        "RU", "CN", "IR", "KP", "SY", "VE", "MM"
    ])

    # News topics to monitor
    news_topics: List[str] = field(default_factory=lambda: [
        "cyberattack", "data breach", "ransomware",
        "geopolitical crisis", "sanctions", "military conflict",
        "critical infrastructure", "supply chain attack",
        "hypersonic missile", "drone warfare", "ballistic missile",
        "military modernization", "arms deal", "defense program",
    ])
