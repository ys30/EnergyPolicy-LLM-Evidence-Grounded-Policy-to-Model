"""Deterministic source-grounded retrieval tests; not LLM or gold accuracy tests."""
import unittest
from hashlib import sha256
from energy_policy_llm.legal_chunker import chunk_legal_text, verify_chunks
from energy_policy_llm.reference_graph import build_reference_graph
from energy_policy_llm.retrievers import BM25LegalRetriever
from energy_policy_llm.evidence_bundle import assemble_evidence, serializable_bundle

LAW = """17.9.571.7 DEFINITIONS:
        A. A distribution cooperative provides retail service.
        B. Renewable certificates are compliance instruments.
17.9.571.8 RENEWABLE PORTFOLIO STANDARD:
        A. A distribution cooperative shall retire renewable energy certificates.
        B. By 2025, forty percent of retail sales must be renewable.
        C. By 2030, fifty percent of retail sales must be renewable.
        D. By 2050, eighty percent applies if reliability and affordability and feasibility.
        F. A generation and transmission cooperative may have duties under 17.9.571.11.
17.9.571.11 CERTIFICATE RULES:
        D. Credits shall be registered in WREGIS under 17.9.571.13(E) and 17.9.571.13(B).
17.9.571.13 ANNUAL REPORT:
        A. Annual reporting shall be submitted by April 30.
"""
SHA = sha256(LAW.encode("utf-8")).hexdigest()

class LegalRagV1Tests(unittest.TestCase):
    def setUp(self):
        self.chunks = chunk_legal_text(LAW, "NM_COOP_2025")
        verify_chunks(LAW, self.chunks)
        self.sections = [c for c in self.chunks if c.subsection is None]
        self.retriever = BM25LegalRetriever([c for c in self.chunks if c.subsection is not None])

    def test_all_sections_are_preserved_and_source_hashed(self):
        self.assertEqual([c.provision for c in self.sections],
            ["17.9.571.7","17.9.571.8","17.9.571.11","17.9.571.13"])
        self.assertTrue(all(c.source_sha256 == SHA for c in self.chunks))
        self.assertTrue(any(c.subsection == "C" and c.provision == "17.9.571.8"
                            for c in self.chunks))

    def test_bm25_returns_citable_evidence(self):
        hits = self.retriever.search("fifty percent retail sales", 3)
        self.assertTrue(hits)
        self.assertIn("fifty percent", hits[0].chunk.exact_text)
        self.assertEqual(hits[0].chunk.subsection, "C")

    def test_parent_context_included(self):
        edges = build_reference_graph(self.chunks)
        bundle = assemble_evidence("fifty percent retail sales", "NM_COOP_2025",
                                  self.retriever,self.chunks,edges,top_k=1)
        self.assertIn("NM_COOP_2025:17.9.571.8", [c.chunk_id for c in bundle.evidence_chunks])
        self.assertEqual(bundle.source_sha256, SHA)
        self.assertNotEqual(bundle.status, "ADJUDICATED")
        self.assertEqual(serializable_bundle(bundle)["source_id"], "NM_COOP_2025")

    def test_flags_ambiguous_reference_without_correcting_it(self):
        flags = {("17.9.571.11","17.9.571.13"): "possible original cross-reference mismatch"}
        edges = build_reference_graph(self.chunks, manually_flagged=flags)
        suspicious=[e for e in edges if e.ambiguity_flag]
        self.assertGreaterEqual(len(suspicious), 2)
        self.assertEqual({e.target_subsection for e in suspicious}, {"B","E"})
        bundle=assemble_evidence("WREGIS registered credits", "NM_COOP_2025",
                                 self.retriever,self.chunks,edges,top_k=1)
        self.assertTrue(bundle.source_ambiguities)
        self.assertNotIn("NM_COOP_2025:17.9.571.13",bundle.graph_expanded_chunks)

    def test_no_results_abstain_and_source_filter(self):
        self.assertEqual(self.retriever.search("quantum zygote", 3), [])
        with self.assertRaisesRegex(ValueError, "No matching evidence"):
            assemble_evidence("quantum zygote","NM_COOP_2025",
                              self.retriever,self.chunks,[],top_k=2)
        self.assertEqual(self.retriever.search("renewable", 4, source_id="NM_IOU"), [])

    def test_mutated_source_rejected(self):
        with self.assertRaisesRegex(ValueError,"hash mismatch"):
            verify_chunks(LAW + "x",self.chunks)

if __name__=="__main__":
    unittest.main()
