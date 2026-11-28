import unittest
from energy_policy_llm.legal_chunker import chunk_legal_text
from energy_policy_llm.retrievers import BM25LegalRetriever
from energy_policy_llm.rag_evaluation import RetrievalCase,evaluate_retrieval

DOC = """17.9.571.8 RENEWABLE PORTFOLIO:
        A. Renewable credits have eligible retirement conditions.
        B. Fifty percent retail renewable sales is targeted.
17.9.571.10 COST EXCEPTIONS:
        A. Cooperative determines the cost threshold each year.
"""
class RetrievalEvalTests(unittest.TestCase):
    def setUp(self):
        self.chunks=chunk_legal_text(DOC,"SYN")
        self.retriever=BM25LegalRetriever([c for c in self.chunks if c.subsection])

    def test_synthetic_recall(self):
        case=RetrievalCase("s1","fifty percent retail",frozenset({"SYN:17.9.571.8:B"}),"SYN")
        out=evaluate_retrieval(self.retriever,[case],k=1)
        self.assertEqual(out["mean_recall_at_k"],1.0)
        self.assertFalse(out["formal_human_gold"])

    def test_guard_against_unadjudicated_gold_metrics(self):
        c=RetrievalCase("s1","cost threshold",frozenset({"SYN:17.9.571.10:A"}),"SYN")
        with self.assertRaisesRegex(ValueError,"human-adjudicated"):
            evaluate_retrieval(self.retriever,[c],require_human_gold=True)

if __name__=="__main__":
    unittest.main()
