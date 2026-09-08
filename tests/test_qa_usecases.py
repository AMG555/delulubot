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
