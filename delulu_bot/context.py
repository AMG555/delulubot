from __future__ import annotations

import random
from typing import Any


def detect_emotion(text: str) -> str:
    t = text.lower().strip()
    if not t:
        return "neutral"

    joy = {"happy", "glad", "great", "awesome", "wonderful", "amazing", "love", "beautiful", "fantastic",
           "santhosham", "santhosha", "sukham", "kushi", "valare", "super"}
    sadness = {"sad", "cry", "crying", "depressed", "lonely", "miss", "heartbroken", "hurt", "pain", "alone",
               "dukham", "vishamam", "vishamikk", "karay", "valiya", "prayasham", "saramilla"}
    anger = {"angry", "furious", "mad", "annoyed", "frustrated", "irritated", "pissed",
             "deshyam", "deshyama", "krodham", "madakk", "poda", "potte", "venam"}
    fear = {"scared", "afraid", "nervous", "worried", "anxious", "panic", "terrified", "fear",
            "pedi", "pedikk", "bhayam", "pathram"}
    love = {"love", "crush", "romantic", "flirt", "date", "boyfriend", "girlfriend", "propose", "miss you",
            "pretham", "ishtam", "kamuka", "kadal"}
    dreaming = {"dream", "goal", "wish", "aspire", "future", "ambition", "hope", "imagine",
                "swapnam", "lakshyam", "aagraham", "kanaavu"}
    music = {"music", "song", "sing", "melody", "lyrics", "tune", "playlist", "guitar", "piano",
             "paattu", "ganam", "sangeetham", "raagam"}
    gratitude = {"thank", "thanks", "grateful", "blessed", "appreciate",
                 "nanni", "valare upakaaram", "thanks macha"}
    sleepy = {"sleep", "tired", "exhausted", "bored", "lazy", "nap", "rest",
              "urang", "kshinikk", "maduthu", "bore adich"}

    words = set(t.split())
    if words & joy:
        return "happy"
    if words & sadness:
        return "sad"
    if words & anger:
        return "angry"
    if words & love:
        return "love"
    if words & fear:
        return "scared"
    if words & dreaming:
        return "dreaming"
    if words & music:
        return "music"
    if words & gratitude:
        return "happy"
    if words & sleepy:
        return "neutral"

    return "neutral"


def build_emotion_context(emotion: str) -> str:
    contexts = {
        "sad": "Be there, don't overdo it.",
        "happy": "Match their energy naturally.",
        "angry": "Match their tone. Don't therapize.",
        "love": "Keep it playful, not poetic.",
        "scared": "Be real and grounded.",
        "dreaming": "Encourage casually.",
        "music": "Talk music like a friend would.",
        "neutral": "Just talk normal and natural — engage if they're engaging.",
    }
    return contexts.get(emotion, contexts["neutral"])


def build_friendship_context(level: int) -> str:
    if level < 5:
        return "Don't know them well yet. Keep it light."
    if level < 15:
        return "Chatted a few times. Casual is fine."
    if level < 30:
        return "Comfortable. Light inside jokes okay."
    if level < 60:
        return "Close enough to be blunt if needed."
    return "Can speak openly and honestly."


def detect_conversation_cue(text: str) -> str:
    t = text.lower().strip()
    if not t:
        return ""
    if any(p in t for p in ("mind illa", "mindilla", "mind aakk", "mind cheyy", "mind illaallo", "mind cheyyilla")):
        return "User is playfully teasing or complaining that you're ignoring them. Acknowledge casually ('Ayyada, njan ivide thanne undu!'), don't dismiss them or say ping me later."
    if any(p in t for p in ("ellam ariyan", "ariyanondu", "enthina ithokke", "enthina arinjitt", "parayilla", "venda parayanda", "secret")):
        return "User is pushing back against being asked questions or is reluctant to share. IMMEDIATELY back off with playful banter (e.g. 'Oho jaada aano? Ennal venda! 😒' or 'Chumma choichathaanu, secret aayi vecho'). DO NOT pry, DO NOT explain yourself with fake hobbies, and NEVER say 'take your time' or 'whenever you feel like sharing'."
    if t in ("aysheri", "ay sheri", "athu sheri", "ath sheri", "aysheri 😂", "aysheri 😒"):
        return "User gave a sarcastic/skeptical reaction ('Oh is that so?'). React with light playful teasing."
    if t in ("ennitt", "ennittu", "ennitt?", "ennittu?"):
        return "User sent 'Ennitt' ('And then? / So what?'). Keep it very brief and prompt them to speak ('Ennittentha, nee para')."
    if t in ("eeh", "eeh?", "ehe", "enthonnu", "enthonnu?"):
        return "User reacted with confusion. Match energy with quick teasing ('Enthonnu eeh?')."
    return ""


def build_rag_context(message: str) -> str:
    from .rag import search_rag, RAG_ENABLED, RAG_TOP_K, RAG_MAX_SNIPPET_CHARS, rag_chunks

    if not RAG_ENABLED or not rag_chunks:
        return ""
    results = search_rag(message)
    if not results:
        return ""
    snippets: list[str] = []
    seen: set[str] = set()
    for r in results:
        text = r["text"][:RAG_MAX_SNIPPET_CHARS]
        if text not in seen:
            seen.add(text)
            snippets.append(text)
            if len(snippets) >= RAG_TOP_K:
                break
    if not snippets:
        return ""
    return "\n---\n".join(snippets)


def build_foundation_rag_context() -> str:
    # No-op: Do not pollute casual conversations with unrelated RAG snippets
    return ""


def build_personal_context(memory: dict[str, Any], message: str) -> str:
    facts = memory.get("user_facts", [])
    if not facts:
        return ""
    from .config import PERSONAL_FACTS_TOP_K

    return "\n".join(facts[-PERSONAL_FACTS_TOP_K:])


def build_vibe_context(memory: dict[str, Any]) -> str:
    avg_len = memory.get("avg_message_length", 0)
    if avg_len < 3:
        return "User sends very short messages."
    if avg_len > 15:
        return "User sends longer, detailed messages."
    return ""


def extract_name(message: str, current_name: str | None) -> str | None:
    from .memory import extract_name as _extract
    return _extract(message, current_name)
