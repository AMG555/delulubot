import io
import pytest
from PIL import Image

from delulu_bot import config
from delulu_bot.context import (
    build_foundation_rag_context,
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
    maybe_extract_user_fact,
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
