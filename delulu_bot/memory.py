from __future__ import annotations

import json
import os
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any

from .config import MEMORY_FILE, PERSONAL_FACTS_LIMIT, PERSONAL_FACTS_TOP_K, logger

user_memories: dict[str, Any] = {}


def load_memories() -> dict[str, Any]:
    global user_memories
    tmp_file = f"{MEMORY_FILE}.tmp"
    if not os.path.exists(MEMORY_FILE) and os.path.exists(tmp_file):
        try:
            os.replace(tmp_file, MEMORY_FILE)
        except Exception:
            pass

    if not os.path.exists(MEMORY_FILE):
        user_memories = {}
        return user_memories
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            user_memories = data
        else:
            user_memories = {}
    except Exception as e:
        logger.warning(f"Failed to load memories: {e}")
        if os.path.exists(tmp_file):
            try:
                with open(tmp_file, "r", encoding="utf-8") as tf:
                    data = json.load(tf)
                if isinstance(data, dict):
                    user_memories = data
                    logger.info("Recovered memories from .tmp backup")
                    return user_memories
            except Exception:
                pass
        user_memories = {}
    return user_memories


def save_memories(memories: dict[str, Any]) -> None:
    try:
        tmp_file = f"{MEMORY_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, MEMORY_FILE)
    except Exception as e:
        logger.error(f"Failed to save memories: {e}")


def get_user_memory(user_id: str) -> dict[str, Any]:
    if user_id not in user_memories:
        user_memories[user_id] = {
            "name": None,
            "conversation_history": [],
            "total_messages": 0,
            "friendship_level": 1,
            "mood_history": [],
            "user_facts": [],
            "active_topics": {},
            "voice_style": "default",
            "voice_enabled": False,
            "tone": "default",
            "lang_style": "manglish",
            "voice_lang": "auto",
            "emoji_level": "default",
        }
    mem = user_memories[user_id]
    if "active_topics" not in mem:
        mem["active_topics"] = {}
    # Normalize legacy "facts" field into "user_facts"
    if "user_facts" not in mem:
        mem["user_facts"] = list(mem.get("facts", []))
    else:
        for f in mem.get("facts", []):
            if f not in mem["user_facts"]:
                mem["user_facts"].append(f)
    # Strip any legacy junk from facts
    mem["user_facts"] = [
        f for f in mem["user_facts"]
        if not any(j in f.lower() for j in JUNK_FACT_FRAGMENTS)
    ]
    return mem


def update_memory(user_id: str, user_message: str, bot_reply: str) -> None:
    memory = get_user_memory(user_id)
    memory["conversation_history"].append({"role": "user", "content": user_message})
    memory["conversation_history"].append({"role": "assistant", "content": bot_reply})
    if len(memory["conversation_history"]) > 50:
        memory["conversation_history"] = memory["conversation_history"][-50:]
    memory["total_messages"] = memory.get("total_messages", 0) + 1
    if memory["total_messages"] % 5 == 0:
        memory["friendship_level"] = min(100, memory.get("friendship_level", 1) + 1)
    save_memories(user_memories)


JUNK_FACT_FRAGMENTS = (
    "story para", "kadhakal", "coffee", "pinne parayam", "onnum illa",
    "chumma", "urang", "urakkam", "poya", "ivide thanne", "entha parayunne",
    "manasilav", "artificial", "talk like human", "talk like a human",
    "samsarikkan ariyilla", "sheeikkum aara", "ith mathre", "choikkan ollo",
    "karyam kettal", "karyam paranjathinu", "ennitt", "aysheri", "beshtt",
)


def maybe_extract_user_fact(message: str) -> str | None:
    lower = message.lower().strip()
    if any(j in lower for j in JUNK_FACT_FRAGMENTS):
        return None
    patterns = [
        r"(?:i\s+(?:am|'m)\s+|ente\s+peru\s+|enne\s+vilikku\s+|call\s+me\s+)(.{2,30})$",
        r"(?:i\s+(?:like|love|enjoy|hate|dislike)\s+(.{2,50}))",
        r"(?:i\s+(?:work|study|live|stay)\s+(?:at|in|as)\s+(.{2,50}))",
        r"(?:my\s+(?:name|job|work|school|college|place|hometown|dream|goal)\s+(?:is|:)\s+(.{2,50}))",
        r"(?:ente\s+(?:joli|place|school|college|dream|goal)\s+(.{2,50}))",
        r"(?:ente\s+(?:oru\s+)?(?:saas|product|app|project|startup|business|company|idea)\s+(.{3,80}))",
        r"(?:(?:saas|product|app|project|startup)\s+(?:ond|und|build|develop|sales|marketing)\s+(.{3,80}))",
        r"(?:(?:hostel|owners|students|clients)\s+(?:vendi|kk vendi)\s+(.{3,80}))",
        r"(?:(?:working|building|developing|doing)\s+(?:on\s+)?(.{3,60}))",
        r"(?:njan\s+(.{3,60}))",
    ]
    for pat in patterns:
        match = re.search(pat, lower)
        if match and match.group(1):
            fact = match.group(1).strip().rstrip(".,!?")
            if len(fact) > 3 and not any(j in fact for j in JUNK_FACT_FRAGMENTS):
                return fact
    return None


def update_user_topics_and_facts(memory: dict[str, Any], message: str) -> None:
    lower = message.lower().strip()
    if not lower or any(j in lower for j in JUNK_FACT_FRAGMENTS):
        return

    if "active_topics" not in memory:
        memory["active_topics"] = {}

    # 1. Hostel app / SaaS
    if "hostel" in lower and any(w in lower for w in ("saas", "app", "mobile app", "product", "sales", "price", "owners", "digital")):
        memory["active_topics"]["hostel_app"] = "Building SaaS mobile app for Kerala hostel owners to digitize them; facing sales and pricing objections"
        add_user_fact(memory, "Building SaaS mobile app for hostel owners in Kerala (struggling with sales/pricing)")

    # 2. General SaaS / Startup
    elif any(w in lower for w in ("saas", "startup", "product")) and any(w in lower for w in ("ond", "und", "build", "develop", "sales", "marketing")):
        memory["active_topics"]["project"] = "Developing and marketing a SaaS product/startup"
        add_user_fact(memory, "Developing and marketing a SaaS product")

    # 3. Trading / Scalping / Chart analysis
    if any(w in lower for w in ("trading", "scalping", "chart analysis", "stock market", "technical analysis")):
        memory["active_topics"]["trading"] = "Interested in stock market trading, technical chart analysis, and scalping"
        add_user_fact(memory, "Interested in stock market trading, chart analysis, and scalping")

    # 4. Standard fact extraction
    fact = maybe_extract_user_fact(message)
    if fact:
        add_user_fact(memory, fact)


def add_user_fact(memory: dict[str, Any], fact: str) -> None:
    if any(j in fact.lower() for j in JUNK_FACT_FRAGMENTS):
        return
    facts = memory.get("user_facts", [])
    for existing in facts:
        if SequenceMatcher(None, fact.lower(), existing.lower()).ratio() > 0.8:
            return
    facts.append(fact)
    if len(facts) > PERSONAL_FACTS_LIMIT:
        facts.pop(0)
    memory["user_facts"] = facts


def clear_user_history(user_id: str) -> None:
    memory = get_user_memory(user_id)
    memory["conversation_history"] = []
    memory["total_messages"] = 0
    memory["friendship_level"] = 1
    memory["mood_history"] = []
    save_memories(user_memories)


def update_user_vibe(memory: dict[str, Any], message: str) -> None:
    word_count = len(message.split())
    memory["avg_message_length"] = (
        0.7 * memory.get("avg_message_length", word_count) + 0.3 * word_count
    )


def extract_name(message: str, current_name: str | None) -> str | None:
    msg_lower = message.lower()
    indicators = [
        "my name is ", "i'm ", "i am ",
        "call me ", "ente peru ", "enne vilikku ",
        "name ", "peru ",
    ]
    for indicator in indicators:
        if indicator in msg_lower:
            idx = msg_lower.index(indicator) + len(indicator)
            remaining = message[idx:].strip()
            if remaining:
                name = remaining.split()[0].strip(".,!?;:")
                if name and len(name) < 30 and not any(c in name for c in "0123456789"):
                    return name
    return None


PAST_INQUIRY_KEYWORDS = (
    "nerathe", "paranja karyam", "paranja karya", "paranjill", "paranjath",
    "ormayundo", "ormayille", "ormilla", "ormayilla", "remember",
    "kurach naal munne", "kurachu naal munne", "maranno", "marannu",
    "last time", "enthayi", "karyam enthayi", "karyam enthaayi",
    "karyam orth", "karyam orma", "karyam ormayundo"
)


def is_user_asking_about_past(user_message: str) -> bool:
    if not user_message:
        return False
    u = user_message.lower()
    return any(k in u for k in PAST_INQUIRY_KEYWORDS)


def strip_unsolicited_past_talk(text: str, user_message: str) -> str:
    # If the user specifically asked or referenced past conversation, DO NOT strip past references!
    if is_user_asking_about_past(user_message):
        return text
    lines = text.split("\n")
    kept: list[str] = []
    for line in lines:
        lower = line.lower().strip()
        if any(p in lower for p in ["remember when you said", "earlier you mentioned"]):
            continue
        kept.append(line)
    return "\n".join(kept)


TRIVIAL_UTTERANCES = {
    "hi", "hello", "hey", "okok", "ok", "ivide thanne unde", "ivide thanne und",
    "sheri", "ahm sheri", "bye", "bst", "best", "eeh", "ennitt", "aysheri",
    "onnum illa", "onnum vendaye", "chill aayi irikk", "sheriyeda",
}


def retrieve_substantive_history(memory: dict[str, Any], query: str, max_items: int = 5) -> str:
    """Find substantive past statements from history so the bot can recall what was discussed."""
    lines: list[str] = []
    active_topics = memory.get("active_topics", {})
    for _, desc in active_topics.items():
        lines.append(f"- [Active ongoing topic]: {desc}")

    history = memory.get("conversation_history", [])
    if not history and not lines:
        return ""

    candidate_turns = history[:-2] if len(history) > 2 else history
    scored_turns: list[tuple[float, str]] = []

    substantive_keywords = {
        "saas", "app", "hostel", "trading", "product", "sales", "project",
        "startup", "work", "job", "client", "market", "pricing", "scalping",
        "chart", "college", "exam", "interview", "money"
    }

    q_lower = (query or "").lower()
    q_words = set(re.findall(r"\w+", q_lower))

    for idx, msg in enumerate(candidate_turns):
        content = msg.get("content", "").strip()
        role = msg.get("role", "user")
        if len(content) < 18:
            continue
        c_lower = content.lower()
        if c_lower in TRIVIAL_UTTERANCES:
            continue
        if any(j in c_lower for j in ("ivide thanne und", "ivide thanne unde", "chumma bore", "kettilla onnude")):
            continue

        c_words = set(re.findall(r"\w+", c_lower))
        score = 1.0 + (idx * 0.05)

        # Content significance bonus
        topic_overlap = c_words & substantive_keywords
        if topic_overlap:
            score += 5.0 * len(topic_overlap)

        # Query word overlap
        q_overlap = c_words & q_words
        if q_overlap:
            score += 3.0 * len(q_overlap)

        prefix = "User previously said" if role == "user" else "Delulu previously replied"
        entry = f'- {prefix}: "{content}"'
        scored_turns.append((score, entry))

    scored_turns.sort(key=lambda x: x[0], reverse=True)
    selected_entries: list[str] = []
    for _, entry in scored_turns[:max_items]:
        if entry not in selected_entries:
            selected_entries.append(entry)

    lines.extend(selected_entries)
    if not lines:
        return ""

    return "\n".join(lines)


load_memories()
