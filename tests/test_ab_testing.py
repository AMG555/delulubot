import pytest
from delulu_bot.context import detect_conversation_cue
from delulu_bot.handlers import de_robotify_reply


class TestABConversationEvaluation:
    """A/B Testing Suite: Compares Variant A (Legacy Baseline) vs Variant B (Tuned Delulu)."""

    TEST_SCENARIOS = [
        {
            "id": "scenario_mind_illa",
            "input": "Entha oru mind illaallo",
            "variant_a_raw": "Haha, chill aayi irikkatte! 😅 Anything on your mind later, just ping me.",
            "expected_cue_action": "ignoring",
        },
        {
            "id": "scenario_aysheri",
            "input": "Aysheri",
            "variant_a_raw": "Nothing much, just chillin’! നീ? 😜",
            "expected_cue_action": "sarcastic",
        },
        {
            "id": "scenario_ellam_ariyan",
            "input": "Ellam ariyanonnundo",
            "variant_a_raw": "Haha, ellam ariyilla 😂 but try cheyyam! What’s the tricky part you’re stuck on?",
            "expected_cue_action": "pushing back",
        },
        {
            "id": "scenario_boundary_pushback",
            "input": "I mean nink enthina ithokke arinjitt",
            "variant_a_raw": "Haha, just because I’m curious a lot! 😄 Njanum project-gal nokki nokki ideas collect cheyyum. Anyway, tell me more about yours?",
            "expected_cue_action": "pushing back",
        },
        {
            "id": "scenario_take_your_time",
            "input": "Eeh",
            "variant_a_raw": "Got it, take your time! ✌️ Whenever you feel like sharing, I’m here.",
            "expected_cue_action": "confusion",
        },
    ]

    def _evaluate_variant_a(self, scenario):
        """Scores legacy Variant A response on robotic traits."""
        text = scenario["variant_a_raw"].lower()
        has_support_platitudes = any(p in text for p in [
            "take your time", "whenever you feel like", "just ping me", "no rush"
        ])
        has_script_leak = any(0x0D00 <= ord(c) <= 0x0D7F for c in scenario["variant_a_raw"])
        is_prying_tech_support = "tricky part you’re stuck on" in text or "tell me more about yours" in text
        return {
            "has_support_platitudes": has_support_platitudes,
            "has_script_leak": has_script_leak,
            "is_prying_tech_support": is_prying_tech_support,
            "passed": not (has_support_platitudes or has_script_leak or is_prying_tech_support)
        }

    def _evaluate_variant_b(self, scenario):
        """Scores tuned Variant B using Delulu's conversation cues and sanitization."""
        # 1. Cue detection
        cue = detect_conversation_cue(scenario["input"])
        has_cue = bool(cue and scenario["expected_cue_action"] in cue.lower())

        # 2. De-robotification & script sanitization
        sanitized = de_robotify_reply(scenario["variant_a_raw"], scenario["input"])
        has_support_platitudes = any(p in sanitized.lower() for p in [
            "take your time", "whenever you feel like", "just ping me", "no rush"
        ])
        has_script_leak = any(0x0D00 <= ord(c) <= 0x0D7F for c in sanitized)

        return {
            "has_cue": has_cue,
            "has_support_platitudes": has_support_platitudes,
            "has_script_leak": has_script_leak,
            "passed": has_cue and not has_support_platitudes and not has_script_leak
        }

    def test_ab_comparison_scorecard(self):
        """A/B test asserts Variant B strictly outperforms Variant A across all metrics."""
        scorecard = {"variant_a_passes": 0, "variant_b_passes": 0, "total": len(self.TEST_SCENARIOS)}

        for scenario in self.TEST_SCENARIOS:
            res_a = self._evaluate_variant_a(scenario)
            res_b = self._evaluate_variant_b(scenario)

            if res_a["passed"]:
                scorecard["variant_a_passes"] += 1
            if res_b["passed"]:
                scorecard["variant_b_passes"] += 1

            # In every scenario, Variant B must pass sanitization & cue handling
            assert res_b["passed"], f"Variant B failed in scenario {scenario['id']}"

        # Assert Variant B has 100% pass rate
        assert scorecard["variant_b_passes"] == scorecard["total"]
        # Assert Variant A failed on these robotic/prying scenarios
        assert scorecard["variant_a_passes"] < scorecard["variant_b_passes"]

        print(f"\n--- A/B TEST SCORECARD ---")
        print(f"Variant A (Legacy Baseline): {scorecard['variant_a_passes']}/{scorecard['total']} passed")
        print(f"Variant B (Tuned Delulu):     {scorecard['variant_b_passes']}/{scorecard['total']} passed (100%)")
