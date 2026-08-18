import unittest

from src.prompt_templates import build_messages, format_context
from src.generator import NoLLM
from src.query_transform import normalize_query
from src.retrieval_utils import reciprocal_rank_fusion, tokenize, top_positive_scores


class RetrievalUtilityTests(unittest.TestCase):
    def test_mixed_language_tokenizer_lowercases_english(self):
        tokens = tokenize("PrEP กับ HIV")
        self.assertIn("prep", tokens)
        self.assertIn("hiv", tokens)
        self.assertTrue(any(token not in {"prep", "hiv"} for token in tokens))

    def test_zero_score_documents_are_not_bm25_candidates(self):
        self.assertEqual(top_positive_scores([0.0, 2.5, -0.1, 1.0], 3), [(1, 2.5), (3, 1.0)])

    def test_weighted_rrf_can_prioritize_the_stronger_retriever(self):
        dense = [0, 1]
        bm25 = [1, 0]

        equal = reciprocal_rank_fusion([dense, bm25], rrf_k=60)
        lexical_first = reciprocal_rank_fusion(
            [dense, bm25],
            weights=[1.0, 1.25],
            rrf_k=60,
        )

        self.assertEqual(equal[0][0], 0)
        self.assertEqual(lexical_first[0][0], 1)

    def test_extra_query_can_be_downweighted_to_limit_query_drift(self):
        fused = reciprocal_rank_fusion(
            [[10], [20]],
            weights=[1.0, 0.7],
            rrf_k=60,
        )
        self.assertEqual(fused[0][0], 10)


class QueryNormalizationTests(unittest.TestCase):
    def test_slang_expansion_preserves_exact_user_words(self):
        normalized = normalize_query("เพร็พหาซื้อที่ไหนครับ")
        self.assertIn("เพร็พ", normalized)
        self.assertIn("PrEP", normalized)
        self.assertNotIn("ครับ", normalized)

    def test_new_alias_adds_formal_medical_terms(self):
        normalized = normalize_query("แข็งค้างหลายชั่วโมง")
        self.assertIn("แข็งค้าง", normalized)
        self.assertIn("priapism", normalized)


class PromptGroundingTests(unittest.TestCase):
    def setUp(self):
        self.chunk = {
            "question": "PrEP คืออะไร",
            "answer": "PrEP เป็นยาป้องกันเอชไอวีก่อนสัมผัสเชื้อ",
        }

    def test_context_keeps_question_and_answer_together(self):
        context = format_context([self.chunk])
        self.assertIn("คำถามในฐานข้อมูล: PrEP คืออะไร", context)
        self.assertIn("คำตอบ: PrEP เป็นยาป้องกัน", context)

    def test_first_source_is_truncated_instead_of_dropped(self):
        context = format_context([self.chunk], max_chars=24)
        self.assertTrue(context)
        self.assertLessEqual(len(context), 24)

    def test_messages_require_grounded_citations(self):
        messages = build_messages("PrEP คืออะไร", [self.chunk])
        self.assertIn("ห้ามเพิ่มความรู้จากภายนอก", messages[0]["content"])
        self.assertIn("[1]", messages[1]["content"])

    def test_no_llm_fallback_returns_the_top_grounded_answer(self):
        answer = NoLLM().chat(build_messages("PrEP คืออะไร", [self.chunk]))
        self.assertEqual(answer, f"{self.chunk['answer']} [1]")


if __name__ == "__main__":
    unittest.main()
