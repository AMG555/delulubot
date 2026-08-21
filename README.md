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
  <a href="#-create-your-own-character">Create Your Character</a> •
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

## Create Your Own Character

Want to fork this bot with your own personality? Here's how:

### 1. Create Character Files in `rag_data/`

**Character Bible** (`rag_data/your_character_bible.md`)
```markdown
# Your Character Name
Age: X | Gender: Y | Personality: Z

## Core Traits
- Trait 1: Description
- Trait 2: Description

## Speech Patterns
- How they talk (formal, casual, slang)
- Signature phrases
- Language mix (if any)

## Background
Brief backstory that shapes their worldview
```

**Lore Document** (`rag_data/your_lore.md`)
- Backstory details
- Relationships
- World-building elements

**Conversation Patterns** (`rag_data/conversation_patterns.md`)
- Example dialogues showing character voice
- How they handle different emotions

### 2. Update Configuration

Edit `.env`:
```env
CHARACTER_BIBLE_FILE=rag_data/your_character_bible.md
RAG_DIR=rag_data
RAG_ENABLED=true
```

### 3. Customize System Prompt

Edit `delulu_bot/prompts.py` → `build_system_instruction()` function to match your character's core personality.

### 4. Test Your Character

```bash
python delulu_bot.py
```

Use these commands to test:
- `/ask <question>` — Test responses
- `/ragsearch <topic>` — Verify RAG retrieval
- `/ragstatus` — Check if files loaded
- `/mood` — Test emotional handling

### Tips for Great Characters

✅ **Be specific** — "talks like a pirate" is better than "friendly"  
✅ **Show, don't tell** — Include example conversations  
✅ **Define boundaries** — What topics they avoid, how formal/casual  
✅ **Add quirks** — Unique phrases, emoji usage, humor style  
✅ **Test edge cases** — How they handle sadness, anger, excitement  

See `rag_data/README.md` for detailed file structure examples.

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
  1. Message @BotFather on Telegram
  2. Send `/newbot` and follow prompts
  3. Copy the bot token
- Groq API key from [Groq Console](https://console.groq.com)
  - Free tier, no credit card required
  - Sign up → Dashboard → Create API Key
- Jina API key(s) from [Jina AI](https://jina.ai/)
  - Free tier: 1M tokens/month per key
  - Sign up → Get API Key
  - You can add multiple keys (comma-separated) for rotation
- (Optional) Google AI Studio API key for Gemini fallback
  - Get from [Google AI Studio](https://aistudio.google.com/apikey)
  - Free tier available

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

### Voice Configuration (Optional)

```env
# Voice Input (transcription)
VOICE_INPUT_ENABLED=true
VOICE_MAX_DURATION_SECONDS=120

# Voice Output (TTS)
VOICE_OUTPUT_ENABLED=true
VOICE_TTS_ENGINE=auto  # auto, edge-tts, gtts
EDGE_TTS_DEFAULT_VOICE=en-IN-NeerjaNeural
EDGE_TTS_SWEET_VOICE=en-US-AriaNeural
VOICE_REPLY_WITH_TEXT=true  # Send both text and voice
AUTO_VOICE_ON_SONG_REQUEST=true
```

### Advanced Configuration

```env
# RAG Settings
RAG_TOP_K=3  # Number of relevant snippets to retrieve
RAG_CHUNK_WORDS=120  # Words per chunk
RAG_MIN_SCORE=1.5  # Minimum relevance score

# Character Guard
CHARACTER_GUARD_ENABLED=true  # Auto-rewrite off-character responses
CHARACTER_GUARD_RETRIES=0  # Number of retry attempts

# Memory
PERSONAL_FACTS_LIMIT=40  # Max facts stored per user
PERSONAL_FACTS_TOP_K=4  # Facts to include in context

# Timeouts
TIMEOUT_SECONDS=60  # API timeout
COMPANION_ALWAYS_ON=true  # Emotional companion mode
```

## Deployment

### Local Development

```bash
# Run locally
python delulu_bot.py

# Or run as module
python -m delulu_bot
```

### Render (Free Tier)

1. **Create Render Account** at [render.com](https://render.com)

2. **Create Web Service**
   - New → Web Service
   - Connect your GitHub/GitLab repo
   - Settings:
     - **Name:** your-bot-name
     - **Environment:** Python
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python delulu_bot.py`

3. **Add Environment Variables**
   - Go to Environment tab
   - Add all variables from `.env.example`:
     - `TELEGRAM_TOKEN`
     - `GROQ_API_KEY`
     - `JINA_API_KEYS`
     - `GEMINI_API_KEY` (optional)
     - All other config variables

4. **Deploy**
   - Render auto-deploys on git push
   - Free tier: 512MB RAM, spins down after 15min idle

### Keep Bot Alive (Render Free Tier)

This bot runs on Render's free plan. Key details:

- **Healthcheck:** Starts an HTTP server on `$PORT`. Root (`/`) returns `OK` when alive, `STARTING` during startup.
- **Diagnostics:** `/dbg` endpoint tests Telegram, Groq, Gemini, Jina, and bot status.
- **Keep Alive:** UptimeRobot pings every 5 minutes to prevent the 15-minute idle sleep.
- **Memory:** 512 MB RAM — `faster-whisper` is excluded to save ~250 MB.

### UptimeRobot Setup

1. Sign up at [uptimerobot.com](https://uptimerobot.com) (free)
2. Add New Monitor:
   - **Monitor Type:** HTTP(s)
   - **URL:** `https://your-bot-name.onrender.com/`
   - **Monitoring Interval:** 5 minutes
   - **Monitor Timeout:** 30 seconds
3. Save — bot will stay awake 24/7

## Project Structure

```
delulubot/
├── delulu_bot/                # Main bot package
│   ├── __main__.py           # Entry point
│   ├── main.py               # Bot initialization
│   ├── handlers.py           # Command & message handlers
│   ├── api_clients.py        # Groq, Gemini, Jina clients
│   ├── config.py             # Configuration loader
│   ├── prompts.py            # System prompts
│   ├── memory.py             # User memory system
│   ├── context.py            # Context builders
│   ├── rag.py                # RAG implementation
│   ├── voice.py              # Voice I/O handling
│   └── webhook_server.py     # Health check server
├── rag_data/                 # Knowledge base
│   ├── README.md             # Character creation guide
│   └── (your character files here)
├── .env                      # Your secrets (gitignored)
├── .env.example              # Config template
├── requirements.txt          # Dependencies
├── user_memories.json        # Per-user data (gitignored)
├── rag_embeddings_cache.json # RAG cache (gitignored)
└── README.md                 # This file
```

## Troubleshooting

### Bot not responding
- Check `/status` command
- Verify API keys in `.env`
- Check logs for errors
- Test with `/ping` (no AI needed)

### Voice not working
- Ensure `VOICE_INPUT_ENABLED=true` and `VOICE_OUTPUT_ENABLED=true`
- Check `edge-tts` is installed: `pip install edge-tts`
- Test with audio message

### RAG not retrieving
- Run `/ragstatus` to check loaded files
- Run `/ragreload` to refresh
- Verify files in `rag_data/`
- Check `JINA_API_KEYS` is set

### Character off-brand
- Enable character guard: `CHARACTER_GUARD_ENABLED=true`
- Check `CHARACTER_BIBLE_FILE` path
- Add more example dialogues in character files
- Review `delulu_bot/prompts.py`

### Out of memory (Render)
- Free tier has 512MB RAM
- Bot optimized for this (no faster-whisper)
- Check for memory leaks in logs

## Contributing

Contributions welcome! Feel free to:
- Report bugs via Issues
- Submit pull requests
- Share your custom characters
- Suggest features

## License

See [LICENSE](LICENSE) file.

## Mirrors

- **GitHub:** https://github.com/amg555/delulubot
- **GitLab:** https://gitlab.com/anniva-group/delulubot

---

<div align="center">
  Made with a touch of Delulu
</div>
