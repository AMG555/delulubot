import io
import pytest
from PIL import Image

from delulu_bot import config
from delulu_bot.context import (
    build_foundation_rag_context,
    build_personal_context,
    build_rag_context,
    detect_conversation_cue,
    detect_emotion,
    extract_name,
)
from delulu_bot.handlers import (
    de_robotify_reply,
    encode_image_bytes_to_base64_jpeg,
)
from delulu_bot.memory import (
    add_user_fact,
    get_user_memory,
    is_user_asking_about_past,
    load_memories,
    maybe_extract_user_fact,
    retrieve_substantive_history,
    save_memories,
    strip_unsolicited_past_talk,
    update_user_topics_and_facts,
    update_user_vibe,
)
from delulu_bot.rag import _load_rag_documents


class TestManglishColloquialComprehension:
    """QA tests for Kerala Manglish slang and conversational cues."""

    def test_mind_illa_cue(self):
        msg = "Entha oru mind illaallo"
        cue = detect_conversation_cue(msg)
        assert "ignoring" in cue.lower()
        assert "ping me later" in cue.lower()

    def test_aysheri_cue(self):
        msg = "Aysheri"
        cue = detect_conversation_cue(msg)
        assert "sarcastic" in cue.lower()

    def test_ellam_ariyanonnundo_cue(self):
        msg = "Ellam ariyanonnundo"
        cue = detect_conversation_cue(msg)
        assert "pushing back" in cue.lower()
        assert "venda" in cue.lower()

    def test_nink_enthina_cue(self):
        msg = "I mean nink enthina ithokke arinjitt"
        cue = detect_conversation_cue(msg)
        assert "pushing back" in cue.lower()
        assert "reluctant" in cue.lower()

    def test_ennitt_cue(self):
        msg = "Ennitt"
        cue = detect_conversation_cue(msg)
        assert "ennitt" in cue.lower()

    def test_eeh_cue(self):
        msg = "Eeh"
        cue = detect_conversation_cue(msg)
        assert "confusion" in cue.lower()

    def test_beshtt_cue(self):
        msg = "Beshtt"
        cue = detect_conversation_cue(msg)
        assert "sarcastic" in cue.lower()

    def test_athenna_cue(self):
        msg = "Athenna"
        cue = detect_conversation_cue(msg)
        assert "why is that" in cue.lower()

    def test_artificial_criticism_cue(self):
        msg = "Feels like artificial"
        cue = detect_conversation_cue(msg)
        assert "criticizing" in cue.lower()
        assert "do not apologize" in cue.lower()

    def test_set_aakkan_criticism_cue(self):
        msg = "Sheri njn nokkatte ninne kurachoode set aakkan pattuo enn"
        cue = detect_conversation_cue(msg)
        assert "criticizing" in cue.lower()
        assert "safety refusals" in cue.lower()

    def test_hehe_laughter_cue(self):
        msg = "hehe"
        cue = detect_conversation_cue(msg)
        assert "laughing" in cue.lower()
        assert "never reply with 'athu sheriyanu'" in cue.lower()

    def test_maduthu_distress_cue(self):
        msg = "Maduthu"
        cue = detect_conversation_cue(msg)
        assert "exhausted" in cue.lower()
        assert "never laugh" in cue.lower()

    def test_kayyinn_poyi_idiom_cue(self):
        msg = "Mothathil kayyinn poyapole"
        cue = detect_conversation_cue(msg)
        assert "out of hand" in cue.lower()
        assert "not physical hand" in cue.lower()

    def test_pidich_keranam_idiom_cue(self):
        msg = "Evdunnelum onn pidich keranam"
        cue = detect_conversation_cue(msg)
        assert "pull themselves together" in cue.lower()

    def test_poya_presence_cue(self):
        msg = "Poya?"
        cue = detect_conversation_cue(msg)
        assert "did you leave" in cue.lower()
        assert "ivide thanne undu" in cue.lower()

    def test_kopp_frustration_cue(self):
        msg = "Kopp"
        cue = detect_conversation_cue(msg)
        assert "frustration" in cue.lower()

    def test_misunderstanding_humility_cue(self):
        msg = "Nink entha paranjitt manasilavathe"
        cue = detect_conversation_cue(msg)
        assert "misunderstanding" in cue.lower()

    def test_paranja_karyam_cue(self):
        msg = "Enthayi njn paranja karyam?"
        cue = detect_conversation_cue(msg)
        assert "past topic" in cue.lower() or "told you earlier" in cue.lower()
        assert "never assume" in cue.lower()

    def test_proper_memory_complaint_cue(self):
        msg = "You dont have any proper memory"
        cue = detect_conversation_cue(msg)
        assert "proper memory" in cue.lower()
        assert "mind illaallo" in cue.lower()

    def test_ith_thanneya_preshnm_cue(self):
        msg = "Ith thanneya preshnm"
        cue = detect_conversation_cue(msg)
        assert "same memory" in cue.lower() or "same mistake" in cue.lower()

    def test_bst_abbreviation_cue(self):
        msg = "Bst"
        cue = detect_conversation_cue(msg)
        assert "sarcastic" in cue.lower()


class TestDeRobotificationAndSanitization:
    """QA tests ensuring robotic phrases and script leaks are stripped."""

    def test_strip_customer_support_platitudes(self):
        robotic_reply = "Got it, take your time! ✌️ Whenever you feel like sharing, I'm here."
        cleaned = de_robotify_reply(robotic_reply, "test")
        assert "take your time" not in cleaned.lower()
        assert "whenever you feel like" not in cleaned.lower()
        assert "i'm here" not in cleaned.lower()

    def test_strip_ping_me_later(self):
        robotic_reply = "Haha, chill aayi irikkatte! Anything on your mind later, just ping me."
        cleaned = de_robotify_reply(robotic_reply, "test")
        assert "just ping me" not in cleaned.lower()
        assert "anything on your mind later" not in cleaned.lower()

    def test_strip_no_rush(self):
        robotic_reply = "no rush! Later when you’re free, tell me about it."
        cleaned = de_robotify_reply(robotic_reply, "test")
        assert "no rush" not in cleaned.lower()

    def test_malayalam_script_transliteration_in_manglish(self):
        mixed_reply = "Nothing much, just chillin’! നീ? 😜"
        cleaned = de_robotify_reply(mixed_reply, "test")
        assert "നീ" not in cleaned
        assert "nee" in cleaned.lower()

    def test_strip_stray_unicode_malayalam(self):
        mixed_reply = "Enthe vishesham എന്താ karyam?"
        cleaned = de_robotify_reply(mixed_reply, "test")
        # Ensure pure Latin output
        assert not any(0x0D00 <= ord(c) <= 0x0D7F for c in cleaned)

    def test_strip_llm_meta_reasoning_leak(self):
        leak_reply = "Athu nannayi! 🎉We have two consecutive final messages, need to pick only one. The last is appropriate.Athu nannayi! 🎉"
        cleaned = de_robotify_reply(leak_reply, "test")
        assert "consecutive final messages" not in cleaned.lower()
        assert "need to pick only one" not in cleaned.lower()
        assert "appropriate" not in cleaned.lower()

    def test_replace_hindi_words_in_manglish(self):
        hindi_reply = "Njan thodi series binge cheyyuva"
        cleaned = de_robotify_reply(hindi_reply, "test")
        assert "thodi" not in cleaned.lower()
        assert "kurachu" in cleaned.lower()

    def test_strip_ai_refusal_robot_phrase(self):
        refusal_reply = "Sorry bro, athu cheyyan pattilla. 🙅♀️"
        cleaned = de_robotify_reply(refusal_reply, "set aakkan nokkatte")
        assert "cheyyan pattilla" not in cleaned.lower()
        assert "sorry" not in cleaned.lower()

    def test_remove_awkward_bro(self):
        bro_reply = "Enth, bro? 🤔"
        cleaned = de_robotify_reply(bro_reply, "Enth")
        assert "bro" not in cleaned.lower()

    def test_strip_agree_bot_on_laughter(self):
        robotic_reply = "Athu sheriyanu 😂"
        cleaned = de_robotify_reply(robotic_reply, "hehe")
        assert "athu sheriyanu" not in cleaned.lower()
        # Should replace with lively tease on the laugh
        assert any(p in cleaned.lower() for p in ("chiri", "theernno", "eda"))

    def test_strip_misplaced_athu_sheriyanu_on_athenna(self):
        robotic_reply = "Athu sheriyanu, later try cheyyam! 😌"
        cleaned = de_robotify_reply(robotic_reply, "Athenna")
        assert "later try cheyyam" not in cleaned.lower()
        assert not cleaned.lower().startswith("athu sheriyanu")

    def test_strip_athu_mind_illa(self):
        robotic_reply = "Athu mind illa, kayy illa, enna? 😅"
        cleaned = de_robotify_reply(robotic_reply, "Kayyiin poi irikkua enn kopp")
        assert "athu mind illa" not in cleaned.lower()
        assert "kayy illa" not in cleaned.lower()

    def test_strip_coffee_advice_on_distress(self):
        distress_reply = "Athu sheriyilla, onnum kurachu chill aayi coffee kudichal mathi! ☕️"
        cleaned = de_robotify_reply(distress_reply, "Mothathil kayyinn poyapole")
        assert "coffee kudichal mathi" not in cleaned.lower()
        assert "njan undo koode" in cleaned.lower()

    def test_strip_laughing_emojis_on_distress(self):
        laugh_in_crisis = "Ayy entha pattiye? 😂 kurachu maathram! 😅"
        cleaned = de_robotify_reply(laugh_in_crisis, "Maduthu")
        assert "😂" not in cleaned
        assert "😅" not in cleaned

    def test_safe_non_empty_fallback(self):
        # Even if input is completely wiped or blank, never return empty
        cleaned = de_robotify_reply("", "test")
        assert cleaned != ""
        assert len(cleaned) > 3

    def test_strip_mind_illaallo_hallucination(self):
        reply = "Sorry da, mind illaallo! 😅 Ennitt, next time kurachu clear aayi para."
        cleaned = de_robotify_reply(reply, "You dont have any proper memory😒")
        assert "mind illaallo" not in cleaned.lower()
        assert "next time kurachu clear aayi para" not in cleaned.lower()
        assert "slip aayi poyi" in cleaned.lower()

    def test_strip_same_problem_robot_dismissal(self):
        reply = "Adu, same problem aayirikkunnu? Enna venam? 🙂"
        cleaned = de_robotify_reply(reply, "Ith thanneya preshnm")
        assert "same problem aayirikkunnu" not in cleaned.lower()
        assert "enna venam" not in cleaned.lower()

    def test_strip_presence_greeting_repetition_as_karyam(self):
        reply = 'Nee paranjathu “Ivide thanne unde” 🙂.'
        cleaned = de_robotify_reply(reply, "Enthayi njn paranja karyam?")
        assert 'ivide thanne unde' not in cleaned.lower()

    def test_strip_unsolicited_past_talk_preserves_solicited_history(self):
        user_msg = "I mean njn nerathe paranja karya ille kurach naal munne"
        bot_reply = "Earlier you mentioned you were building a mobile app for hostel owners in Kerala."
        cleaned = strip_unsolicited_past_talk(bot_reply, user_msg)
        assert "earlier you mentioned" in cleaned.lower()
        assert "hostel owners" in cleaned.lower()

    def test_strip_mone_and_makale_vocatives(self):
        reply = "Entha mone ninte problem? Enta mone, enthokkeya parayunne? Makale chill aavu."
        cleaned = de_robotify_reply(reply, "test")
        assert "mone" not in cleaned.lower()
        assert "makale" not in cleaned.lower()
        assert "eda" in cleaned.lower()

    def test_strip_tamil_koncham_words(self):
        reply = "Koncham basic ariyum, athu koncham complex aanu."
        cleaned = de_robotify_reply(reply, "test")
        assert "koncham" not in cleaned.lower()
        assert "kurachu" in cleaned.lower()

    def test_limit_question_stacking(self):
        reply = "Okok? Enthokkeya vishesham? Ninte plans entha? Pwoli aanu ennano? 😄"
        cleaned = de_robotify_reply(reply, "Okok")
        assert cleaned.count("?") <= 1
        assert "enthokkeya vishesham" in cleaned.lower()

    def test_strip_bestie_cringe_and_compliance(self):
        reply = "Oru paadu! Njan ingane artificial aaytt samsarikkunno? 🥺 Njan ninte bestie aanu, entha doubt? 😜 Ninte ishtam pole samsarikkan njan try cheyyunnundallo."
        cleaned = de_robotify_reply(reply, "Ni entha ingane artificial aaytt samsarikkunne")
        assert "bestie aanu" not in cleaned.lower()
        assert "try cheyyunnundallo" not in cleaned.lower()
        assert "🥺" not in cleaned


class TestRAGPipelineCleanliness:
    """QA tests ensuring RAG doesn't leak developer docs or pollute casual chat."""

    def test_readme_excluded_from_rag(self):
        docs = _load_rag_documents()
        for doc in docs:
            assert "# RAG Data Folder" not in doc
            assert "## Creating Your Own Character" not in doc

    def test_foundation_rag_does_not_pollute_casual_chat(self):
        foundation = build_foundation_rag_context()
        assert foundation == ""


class TestVisionPipeline:
    """QA tests for image, GIF thumbnail, and sticker encoding."""

    def test_image_encoder_rgb_conversion(self):
        # Create an RGBA image
        img = Image.new("RGBA", (200, 200), color=(255, 0, 0, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = encode_image_bytes_to_base64_jpeg(buf.getvalue())
        assert isinstance(b64, str)
        assert len(b64) > 50

    def test_image_encoder_resizing(self):
        # Create an oversized image
        img = Image.new("RGB", (2000, 1500), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        b64 = encode_image_bytes_to_base64_jpeg(buf.getvalue(), max_dim=800)
        assert isinstance(b64, str)
        assert len(b64) > 50

    def test_webp_sticker_conversion(self):
        # Create a WebP sticker
        img = Image.new("RGB", (128, 128), color="green")
        buf = io.BytesIO()
        img.save(buf, format="WEBP")
        b64 = encode_image_bytes_to_base64_jpeg(buf.getvalue())
        assert isinstance(b64, str)
        assert len(b64) > 50


class TestMemoryAndEmotionTracking:
    """QA tests for user memory, fact extraction, and emotion cues."""

    def test_emotion_detection(self):
        assert detect_emotion("Njan aake sad aanu") == "sad"
        assert detect_emotion("Super happy today") == "happy"
        assert detect_emotion("Kore deshyam varunnu") == "angry"
        assert detect_emotion("Just doing some projects") == "neutral"
        assert detect_emotion("Maduthu") == "sad"
        assert detect_emotion("Mothathil kayyinn poyapole") == "sad"
        assert detect_emotion("Totally down") == "sad"

    def test_fact_extraction(self):
        fact = maybe_extract_user_fact("I work as a software engineer")
        assert fact is not None
        assert "software engineer" in fact.lower()

    def test_name_extraction(self):
        name = extract_name("My name is Amal", None)
        assert name == "Amal"

    def test_vibe_profile_updating(self):
        mem = get_user_memory("qa_user_test_123")
        update_user_vibe(mem, "short msg")
        assert "avg_message_length" in mem
        assert mem["avg_message_length"] > 0

    def test_project_and_saas_fact_extraction(self):
        fact = maybe_extract_user_fact("ente oru saas product ond athil sales kond varanam")
        assert fact is not None
        assert "sales kond varanam" in fact.lower()

    def test_substantive_history_retrieval(self):
        mem = {
            "conversation_history": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hi! Evide poyi?"},
                {"role": "user", "content": "Alla ith kerala aa ivdatge hostel ownersokke ippalum digital aayttilla so avrkk vendi oru mobile app aa"},
                {"role": "assistant", "content": "Hostel owners-ine convince cheyyanam, that is the tough part"},
                {"role": "user", "content": "Ivide thanne unde"},
                {"role": "assistant", "content": "Sheri, evide busy aayi?"},
            ]
        }
        retrieved = retrieve_substantive_history(mem, "Enthayi njn paranja karyam?")
        assert "hostel owners" in retrieved.lower()
        assert "ivide thanne unde" not in retrieved.lower()

    def test_ishtam_does_not_trigger_romantic_love(self):
        msg = "Aaa nink ishtam ulla enthe engilum patti para kekkatte"
        assert detect_emotion(msg) == "neutral"

    def test_valare_and_valiya_do_not_trigger_false_emotions(self):
        assert detect_emotion("Valare busy aanu") == "neutral"
        assert detect_emotion("Valiya project aanu") == "neutral"

    def test_update_user_topics_hostel_saas_and_trading(self):
        mem = {"user_facts": [], "active_topics": {}}
        update_user_topics_and_facts(
            mem,
            "Alla ith kerala aa ivdatge hostel ownersokke ippalum digital aayttilla so avrkk vendi oru mobile app aa. Avr parayunnath over priced aanenna"
        )
        assert "hostel_app" in mem["active_topics"]
        assert "hostel owners" in mem["active_topics"]["hostel_app"].lower()
        assert any("hostel" in f.lower() for f in mem["user_facts"])

        update_user_topics_and_facts(mem, "Scalping cheytha kollaam ennund help cheyyo, chart analysis ariyavo")
        assert "trading" in mem["active_topics"]
        assert "scalping" in mem["active_topics"]["trading"].lower()

    def test_junk_fact_exclusion(self):
        mem = {"user_facts": [], "active_topics": {}}
        update_user_topics_and_facts(mem, "Story para ninte")
        update_user_topics_and_facts(mem, "Njan oru coffee kudikkuva")
        update_user_topics_and_facts(mem, "Ni entha ingane artificial aaytt samsarikkunne")
        assert len(mem["user_facts"]) == 0
        assert len(mem["active_topics"]) == 0

    def test_build_personal_context_active_topics(self):
        mem = {
            "user_facts": ["Interested in trading"],
            "active_topics": {"hostel_app": "Building SaaS mobile app for hostel owners"}
        }
        ctx = build_personal_context(mem, "Hi")
        assert "ACTIVE USER TOPICS" in ctx
        assert "hostel owners" in ctx.lower()
        assert "KNOWN USER FACTS" in ctx
        assert "trading" in ctx.lower()

    def test_atomic_memory_persistence(self, tmp_path, monkeypatch):
        test_file = str(tmp_path / "test_user_memories.json")
        monkeypatch.setattr("delulu_bot.memory.MEMORY_FILE", test_file)
        data = {"user_1": {"name": "TestUser", "user_facts": ["Coding in Python"]}}
        save_memories(data)
        loaded = load_memories()
        assert "user_1" in loaded
        assert loaded["user_1"]["name"] == "TestUser"

    def test_vision_caption_topic_extraction(self):
        mem = {"user_facts": [], "active_topics": {}}
        update_user_topics_and_facts(mem, "ente hostel mobile app screenshot nokku")
        assert "hostel_app" in mem["active_topics"]

    def test_gemini_contents_alternation_safety(self):
        recent = [
            {"role": "assistant", "content": "Intro"},
            {"role": "user", "content": "First msg"},
            {"role": "user", "content": "Second msg"},
            {"role": "assistant", "content": "Reply"},
        ]
        user_message = "Current text"
        contents = []
        for msg in recent:
            role = "user" if msg["role"] == "user" else "model"
            text_part = (msg.get("content") or "").strip()
            if not text_part:
                continue
            if not contents:
                if role == "model":
                    continue
                contents.append({"role": role, "parts": [text_part]})
            else:
                if contents[-1]["role"] == role:
                    contents[-1]["parts"][0] += f"\n{text_part}"
                else:
                    contents.append({"role": role, "parts": [text_part]})
        if contents and contents[-1]["role"] == "user":
            contents[-1]["parts"][0] += f"\n{user_message}"
        else:
            contents.append({"role": "user", "parts": [user_message]})

        assert len(contents) > 0
        assert contents[0]["role"] == "user"
        for i in range(len(contents) - 1):
            assert contents[i]["role"] != contents[i + 1]["role"]
        assert contents[-1]["role"] == "user"

    def test_rolling_conversation_summary_archiving(self):
        from delulu_bot.memory import update_memory, get_user_memory
        mem = get_user_memory("rolling_test_user")
        mem["conversation_history"] = []
        mem["conversation_summary"] = ""

        # Populate with 26 exchanges (52 turns)
        for i in range(26):
            update_memory(
                "rolling_test_user",
                f"I am working on building scalable microservice module number {i}",
                f"That sounds great, keep going with microservice module number {i}"
            )
        assert len(mem["conversation_history"]) == 40
        assert mem["conversation_summary"] != ""
        assert "microservice module number" in mem["conversation_summary"]

    def test_manglish_name_patterns(self):
        assert extract_name("Amal aanu ente peru", None) == "Amal"
        assert extract_name("Njan Rahul aanu", None) == "Rahul"
        assert extract_name("Njan ivide aanu", None) is None  # ivide is filtered
        assert extract_name("Ath aanu ente peru", None) is None  # ath is filtered

    def test_life_facts_and_category_dedup(self):
        mem = {"user_facts": [], "active_topics": {}}
        update_user_topics_and_facts(mem, "Enikku oru patti undu peru Bruno")
        assert any("Bruno" in f for f in mem["user_facts"])

        update_user_topics_and_facts(mem, "Ente veedu Thrissur aanu")
        assert any("Thrissur" in f for f in mem["user_facts"])

        # Update location to Kochi - should replace Thrissur, not duplicate
        update_user_topics_and_facts(mem, "Ente veedu Kochi aanu")
        loc_facts = [f for f in mem["user_facts"] if "Location/Hometown:" in f]
        assert len(loc_facts) == 1
        assert "Kochi" in loc_facts[0]

    def test_favourite_and_birthday_fact_extraction(self):
        mem = {"user_facts": [], "active_topics": {}}
        update_user_topics_and_facts(mem, "Ente fav food biriyani aanu")
        assert any("biriyani" in f.lower() for f in mem["user_facts"])

        update_user_topics_and_facts(mem, "My birthday is on 15 August")
        assert any("15 august" in f.lower() for f in mem["user_facts"])

    def test_query_relevant_facts_prioritization(self):
        mem = {
            "user_facts": [
                "Has a pet: dog named Bruno",
                "Work/Study: Python developer",
                "Location/Hometown: Kochi",
                "Interested in stock market trading",
                "Life event: AWS certification exam next week",
            ],
            "active_topics": {},
        }
        # Ask about pet: dog named Bruno should be prioritized into top-K even though it's oldest
        ctx = build_personal_context(mem, "Ente pattiye ormayundo? Peru entha?")
        assert "Bruno" in ctx

        # Ask about exam: exam fact should be prioritized
        ctx_exam = build_personal_context(mem, "Nale exam undu tension")
        assert "exam" in ctx_exam.lower()

    def test_user_id_int_and_str_interchangeability(self):
        mem_int = get_user_memory(987654321)
        mem_str = get_user_memory("987654321")
        assert mem_int is mem_str

        mem_int["name"] = "UnifiedUser"
        assert get_user_memory("987654321")["name"] == "UnifiedUser"

    def test_preferred_name_preservation(self):
        mem = get_user_memory("preserve_user")
        mem["name"] = "Appu"
        # Simulate message handler logic: if first_name exists but memory has name, keep Appu
        tg_first_name = "Amal George"
        if tg_first_name and not mem.get("name"):
            mem["name"] = tg_first_name
        assert mem["name"] == "Appu"

    def test_past_inquiry_keywords_expansion(self):
        assert is_user_asking_about_past("Ormando enne?")
        assert is_user_asking_about_past("Ormundo?")
        assert is_user_asking_about_past("Maranno enne?")
        assert is_user_asking_about_past("Ente peru entha?")
        assert is_user_asking_about_past("Njan aara?")
        assert is_user_asking_about_past("What is my name?")

    def test_forget_clears_all_legacy_and_summary(self):
        mem = get_user_memory("forget_test_user")
        mem["user_facts"] = ["fact 1"]
        mem["facts"] = ["legacy fact 1"]
        mem["active_topics"] = {"proj": "topic"}
        mem["conversation_summary"] = "- User: something important"

        # Simulate forget command
        mem["user_facts"] = []
        mem["facts"] = []
        mem["active_topics"] = {}
        mem["conversation_summary"] = ""

        # Re-fetching memory should not resuscitate facts from legacy
        refetched = get_user_memory("forget_test_user")
        assert len(refetched["user_facts"]) == 0
        assert len(refetched["active_topics"]) == 0
        assert refetched["conversation_summary"] == ""

    def test_remember_name_integration(self):
        mem = get_user_memory("remember_name_user")
        text = "call me Appu"
        new_name = extract_name(text, mem.get("name"))
        if new_name:
            mem["name"] = new_name
        add_user_fact(mem, text)
        assert mem["name"] == "Appu"
        assert any("Appu" in f or "call me" in f.lower() for f in mem["user_facts"])


