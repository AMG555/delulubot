from __future__ import annotations

import random
from typing import Any


def detect_emotion(text: str) -> str:
    t = text.lower().strip()
    if not t:
        return "neutral"

    sad_phrases = (
        "sheriyavunnilla", "kayyinn", "kayyiin", "kayyinu", "nadapadi aavilla",
        "nadapadi aavoonn", "totally down", "mothathil lost", "lost aayi", "lost aayitt",
        "pidich keranam", "pidichu keranam", "life kayyinn", "aake maduthu", "onnum sheriyavunnilla",
        "going bad", "going downhill", "lost everything", "maduthu", "maduth"
    )
    if any(p in t for p in sad_phrases):
        return "sad"

    joy = {"happy", "glad", "great", "awesome", "wonderful", "amazing", "beautiful", "fantastic",
           "santhosham", "santhosha", "sukham", "kushi", "super"}
    sadness = {"sad", "cry", "crying", "depressed", "lonely", "miss", "heartbroken", "hurt", "pain", "alone",
               "dukham", "vishamam", "vishamikk", "karay", "prayasham", "saramilla",
               "maduthu", "maduth", "maduthitt", "down", "lost", "theernnu", "kopp"}
    anger = {"angry", "furious", "mad", "annoyed", "frustrated", "irritated", "pissed",
             "deshyam", "deshyama", "krodham", "madakk", "poda"}
    fear = {"scared", "afraid", "nervous", "worried", "anxious", "panic", "terrified", "fear",
            "pedi", "pedikk", "bhayam", "pathram"}
    love = {"love", "crush", "romantic", "flirt", "date", "boyfriend", "girlfriend", "propose", "miss you",
            "pranayam", "kamukan", "kamuki"}
    dreaming = {"dream", "goal", "wish", "aspire", "future", "ambition", "hope", "imagine",
                "swapnam", "lakshyam", "aagraham", "kanaavu"}
    music = {"music", "song", "sing", "melody", "lyrics", "tune", "playlist", "guitar", "piano",
             "paattu", "ganam", "sangeetham", "raagam"}
    gratitude = {"thank", "thanks", "grateful", "blessed", "appreciate",
                 "nanni", "valare upakaaram", "thanks macha"}
    sleepy = {"sleep", "tired", "exhausted", "bored", "lazy", "nap", "rest",
              "urang", "kshinikk"}

    words = set(t.split())
    if words & sadness:
        return "sad"
    if words & joy:
        return "happy"
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
        "sad": "User is going through a hard time, feeling lost, overwhelmed, or down. Be a real caring friend: listen warmly, validate their feelings ('Ayy entha pattiye da?', 'Njan undo koode'), don't give cheap motivational quotes, never tell them to just drink coffee or chill, and NEVER laugh or use laughing emojis (no 😂, no 😅, no 🙃).",
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
    if any(p in t for p in ("maduthu", "aake maduthu", "maduth")):
        return "User is deeply exhausted, overwhelmed, or burned out ('Maduthu'). Empathize with real warmth ('Ayy entha pattiye da?', 'Aake madutho? Entha scene?'). NEVER laugh (NO 😂, NO 😅), NEVER tell them to just drink coffee, and do NOT dismiss their feelings."
    if any(p in t for p in ("kayyinn", "kayyiin", "kayyinu", "life kayyinn")):
        return "User is saying things are completely out of hand ('kayyinnu poyi' is an idiom meaning lost control, NOT physical hand!). Empathize with their distress: 'Enthaada ithra scene aayath, para', 'Njan kelkkam eda'. DO NOT take 'kayy' literally as hand, and NEVER say 'Athu mind illa'!"
    if any(p in t for p in ("pidich keranam", "pidichu keranam")):
        return "User wants to pull themselves together / get life back on track ('pidichu keranam' means finding footing/recovering, NOT physical climbing!). Support them warmly: 'Pattum eda, set aakkam', 'Entha aadyam cheyyende para'. NEVER say 'Athu venda'!"
    if any(p in t for p in ("nadapadi aavoonn", "nadapadi aavilla", "sheriyavunnilla", "totally down", "mothathil lost")):
        return "User feels hopeless or lost in life. Offer gentle presence and listening ('Angane parayalle eda, enthelum vazhi kaanum. Entha pattiye?'). DO NOT suggest coffee or tell them to chill."
    if t in ("poya?", "poyo?", "evide poyi", "evide poyatha", "evdya"):
        return "User is asking 'Did you leave / Are you there?'. Confirm immediately with warmth: 'Ivide thanne undu eda, net oru second slow aayatha! Para, njan kelkkunnu.'"
    if t in ("kopp", "koppaanu", "enn kopp") or "kopp" in t.split():
        return "User is expressing strong frustration ('Kopp'). Acknowledge their anger: 'Deshyam varunnathil thettilla eda, entha pattiye?'. Never dismiss with 'Athu mind illa'."
    if any(p in t for p in ("manasilav", "manassilav", "prayojanom", "prayojanam", "human allallo", "parayunnath polum")):
        return "User is frustrated that you are misunderstanding them or feeling you don't help. DO NOT defend yourself ('Njan real friend aane, robot alla')! Apologize with real friend humility: 'Sorry da, njan chumma alamb aakki. Nee nalla tensionil aanennu manasilavunnu. Njan full kelkkan ready aanu, para entha pattiye'."
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
    if any(p in t for p in ("athenna", "athentha", "athe entha")):
        return "User is asking 'Why is that? / Why not?'. Give a direct casual human reason, never say 'Athu sheriyanu, later try cheyyam'."
    if any(p in t for p in ("paranja karyam", "paranja karya", "nerathe paranja", "kurach naal munne", "kurachu naal munne", "enthayi njn paranja", "karyam enthayi")):
        return "User is asking about something they told you earlier ('paranja karyam' / 'nerathe paranja' / past topic). NEVER assume this refers to recent trivial greetings like 'ivide thanne undu'! Check past conversation topics and user facts (e.g. app, startup, project, work). If you recall it, refer to it naturally ('Aa hostel app-inte karyam aano?'). If unsure, ask casually which topic they meant without pretending you didn't hear."
    if any(p in t for p in ("proper memory", "memory illa", "ormayille", "ormayundo", "marannu poyo", "maranno", "ormilla")):
        return "User is asking if you remember or complaining about your memory ('nink ormayille', 'proper memory illa'). NEVER say 'mind illaallo' (that is broken Manglish)! NEVER blame the user ('clear aayi para'). Own it casually with friend humility: 'Ayy sorry da, slip aayi poyi! Entha karyam onnude para, njan kelkkam'. DO NOT act dismissive ('enna venam?')."
    if any(p in t for p in ("ith thanneya preshnm", "ith thanne preshnm", "ith thanneya problem", "ath thanneya preshnm")):
        return "User is frustrated that you made the same memory or comprehension mistake ('Ith thanneya preshnm'). DO NOT say 'Adu, same problem aayirikkunnu? Enna venam?' or act like a robot! Apologize warmly: 'Sorry da, njan chumma alamb aakki. Entha karyam para, njan set aakkam'."
    if any(p in t for p in ("beshtt", "besht", "best-tt")) or t in ("best", "beshtt", "besht", "bst"):
        return "User is being sarcastic ('Beshtt' / 'Bst' / 'Oh great... 😒'). Do NOT take this as praise! Reply with spontaneous wry banter ('Pinne!', 'Enthonnu best 😒', 'Ninakku parayan eluppamaa 😂', 'Jaada aano?'). Do NOT repeat the exact same reply every time."
    laugh_tokens = {"hehe", "haha", "hahaha", "hehehe", "lol", "lmao", "rofl", "kikiki", "chiri", "hehe 😂", "haha 😂"}
    if t in laugh_tokens or any(p in t for p in ("hehe", "haha", "hahaha")) or any(c in t for c in "😂🤣😆😹"):
        return "User is chuckling or laughing ('hehe' / 'haha'). NEVER reply with 'Athu sheriyanu', 'Sheri', or blind agreement! Tease them about laughing ('Chirichu theernno? 😂', 'Enthaada itra chiri?', 'Vattaano ninakku', 'Enthonnu chiri 😒') or drop a dry reaction."
    if any(p in t for p in ("artificial", "improve aakan", "manglish athra pora", "need to fix", "poraa", "set aakkan", "set aakan", "fix aakkan")):
        return "User is criticizing your texting, calling you artificial, or offering to 'fix' you. DO NOT apologize, DO NOT say 'sorry bro', DO NOT say 'trying to be a real friend', and DO NOT give AI assistant safety refusals ('athu cheyyan pattilla'). React with sassy confidence like a real friend ('Ente Manglish-inu enthaada kuzhappam? 😂 Njan inganene aanu' or 'Nee aara enne set aakkan? 😜')."
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
    facts = list(memory.get("user_facts", []))
    for f in memory.get("facts", []):
        if f not in facts and not f.startswith("Loves: story"):
            facts.append(f)
    active_topics = memory.get("active_topics", {})

    lines: list[str] = []
    if active_topics:
        lines.append("ACTIVE USER TOPICS & PROJECTS:")
        for _, topic_desc in active_topics.items():
            lines.append(f"- {topic_desc}")

    if facts:
        from .config import PERSONAL_FACTS_TOP_K
        if lines:
            lines.append("KNOWN USER FACTS:")
        for fact in facts[-PERSONAL_FACTS_TOP_K:]:
            lines.append(f"- {fact}")

    return "\n".join(lines)


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
