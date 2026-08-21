<div align="center">

<img src="https://img.shields.io/badge/Version-5.0_(Multi--Language)-FF6B35?style=for-the-badge&logo=groq&logoColor=white" alt="Version Badge"/>
<img src="https://img.shields.io/badge/Platform-Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Badge"/>
<img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>

<h1 align="center">Delulubot</h1>
<h3 align="center">Your Sassy Manglish AI Companion on Telegram</h3>

<p align="center">
  100% free-tier conversational AI bot — Groq (primary) + Jina (embeddings) + Gemini (fallback). Featuring RAG personality grounding, multi-language voice, and persistent per-user customization.
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-commands">Commands</a> •
  <a href="#-user-customization">Customization</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-deployment">Deployment</a>
</p>
</div>

---

## Overview

**Delulubot** is a Telegram chatbot that acts as "Delulu", a 23-year-old sassy girl who speaks in **Manglish** (Malayalam + English). Users can change her language style to Hinglish, Tanglish, pure English, and more.

Built on a **multi-provider free-tier architecture**: Groq for primary chat, Jina AI for RAG embeddings, and Google Gemini as fallback. No credit card required.

## Features

| Feature | Description |
| :--- | :--- |
| **RAG Architecture** | Grounds the bot in custom knowledge using Jina AI embeddings for lore and personality consistency. |
| **Multi-Language Voice** | 12 languages for voice output (English, Malayalam, Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Spanish, French, German). Auto-detects script or user can set manually. |
| **User Customization** | Per-user tone, language style, voice language, emoji frequency — all persisted across sessions. |
| **Persistent Memory** | Remembers facts, conversation history, mood trends, and friendship level per user. |
| **Personality Guard** | System prompt + character bible prevent persona drift. Auto-rewrites if style breaks character. |
| **Multi-Provider Fallback** | Groq (primary) → Gemini (fallback) with Jina key rotation for rate limits. |
| **Auto-Restart** | Crash-proof loop with diagnostic logging via `/dbg` healthcheck. |
| **Health Monitoring** | Built-in HTTP server for Render + UptimeRobot. |

## Commands

| Command | What it does |
| :--- | :--- |
| `/start` | Welcome message |
| `/companion` | Quick usage guide |
| `/settings` | Show all your current preferences |
| `/tone <style>` | Change conversation tone (default, sweet, romantic, funny, serious, stoic, chill) |
| `/langstyle <style>` | Change language mix (manglish, hinglish, english, tanglish, tenglish, kanglish) |
| `/voicelang <code>` | Set voice language (auto, en, ml, hi, ta, te, kn, bn, mr, gu, es, fr, de) |
| `/voice on\|off\|sweet\|default` | Voice reply mode & style |
| `/emoji none\|default\|high` | Control emoji frequency |
| `/ping` | Quick connectivity test (no AI needed) |
| `/ask <question>` | Ask Delulu for advice |
| `/mood` | Emotional check-in |
| `/remember <fact>` | Save something about you |
| `/aboutme` | See what Delulu remembers |
| `/forget` | Remove a saved fact |
| `/sing` | Ask Delulu to sing |
| `/music` | Creative boost |
| `/random` | Random Delulu thought |
| `/status` | Check bot status |
| `/ragstatus` | Check RAG index |
| `/ragsearch` | Search knowledge docs |
| `/ragreload` | Reload knowledge docs |
| `/clearhistory` | Reset conversation |

## User Customization

Each user has persistent preferences stored in `user_memories.json`:

**Tone** — Change how Delulu talks to you:
- `default` — Casual Manglish, sassy but warm
- `sweet` — Soft and affectionate
- `romantic` — Flirty and charming
- `funny` — Extra humorous
- `serious` — Mature and grounded
- `stoic` — Minimal and direct
- `chill` — Super relaxed

**Language Style** — Change the language mix:
- `manglish` — Malayalam + English (default)
- `hinglish` — Hindi + English
- `english` — Pure English
- `tanglish` — Tamil + English
- `tenglish` — Telugu + English
- `kanglish` — Kannada + English

**Voice Language** — 12 options including auto-detect based on text script.

**Emoji Level** — `none`, `default` (0-1 per message), or `high` (1-3 per message).

## Tech Stack

- **Core:** Python 3.9+
- **Primary Chat:** Groq (openai/gpt-oss-120b) via OpenAI SDK
- **Embeddings:** Jina AI (jina-embeddings-v3) with key rotation
- **Fallback Chat:** Google Gemini (gemini-2.0-flash-lite)
- **Bot Framework:** python-telegram-bot v20+
- **TTS:** edge-tts (primary), gTTS (fallback) — no faster-whisper (removed for RAM)
- **Async:** asyncio
- **Monitoring:** Built-in HTTP healthcheck + UptimeRobot
- **Hosting:** Render (free plan, 512 MB RAM)

## Installation

### Prerequisites
- Python 3.9+
- Telegram bot token from [@BotFather](https://t.me/botfather)
- Groq API key from [Groq Console](https://console.groq.com)
- Jina API key(s) from [Jina AI](https://jina.ai/) — 1+ keys
- (Optional) Google AI Studio API key for Gemini fallback

### Setup

```bash
git clone https://github.com/amg555/delulubot.git
cd delulubot
python -m venv venv
# Windows: venv\Scripts\activate
# Linux:   source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Run:
```bash
python delulu_bot.py
```

## Configuration

Key environment variables in `.env`:

```env
TELEGRAM_TOKEN=your_token_here
GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-120b
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.0-flash-lite
JINA_API_KEYS=key1,key2,key3
JINA_MODEL=jina-embeddings-v3
RAG_ENABLED=true
RAG_DIR=rag_data
CHARACTER_BIBLE_FILE=rag_data/delulu_character_bible.md
VOICE_TTS_ENGINE=auto
TIMEOUT_SECONDS=60
```

Full reference in `.env.example`.

## Deployment

### Render (Free Tier)

This bot runs on Render's free plan. Key details:

- **Healthcheck:** Starts an HTTP server on `$PORT`. Root (`/`) returns `OK` when alive, `STARTING` during startup.
- **Diagnostics:** `/dbg` endpoint tests Telegram, Groq, Gemini, Jina, and bot status.
- **Keep Alive:** UptimeRobot pings every 5 minutes to prevent the 15-minute idle sleep.
- **Memory:** 512 MB RAM — `faster-whisper` is excluded to save ~250 MB.

### UptimeRobot

Monitor at `https://delulubot-6b5v.onrender.com/` with HEAD requests every 5 minutes.

## Project Structure

```
delulubot/
├── rag_data/                  # Knowledge base & character bible
├── .env                       # Environment variables (gitignored)
├── .env.example               # Configuration template
├── delulu_bot.py              # Main application (~3700 lines)
├── requirements.txt           # Python dependencies
├── user_memories.json         # Per-user persistent data
├── rag_embeddings_cache.json  # Cached Jina embeddings
└── README.md                  # This file
```

## Mirrors

- **GitHub:** https://github.com/amg555/delulubot
- **GitLab:** https://gitlab.com/anniva-group/delulubot

---

<div align="center">
  Made with a touch of Delulu
</div>
