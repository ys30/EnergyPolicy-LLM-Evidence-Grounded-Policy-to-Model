import unittest
from hashlib import sha256
from energy_policy_llm.legal_chunker import chunk_legal_text
from energy_policy_llm.hybrid_retrieval import HybridRetriever, cosine
from energy_policy_llm.reference_graph import build_reference_graph
from energy_policy_llm.retrievers import BM25LegalRetriever
from energy_policy_llm.evidence_bundle import assemble_evidence
from energy_policy_llm.field_evidence import FieldEvidence,validate_field_evidence

TEXT="""17.9.571.8 RENEWABLE PORTFOLIO:
        B. By 2025, forty percent of New Mexico retail sales must be renewable.
        C. By 2030, fifty percent of retail sales must be renewable.
17.9.571.10 REASONABLE COST:
        A. Cost threshold sixty dollars per MWh.
"""
class HybridEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.chunks=chunk_legal_text(TEXT,"NM_COOP")
        self.subs=[c for c in self.chunks if c.subsection is not None]

    def test_bm25_only_does_not_claim_semantic_embedding(self):
        retriever=HybridRetriever(self.subs)
        hits=retriever.search("fifty percent retail sales",k=3)
        self.assertEqual(hits[0].chunk.subsection,"C")
        self.assertEqual(hits[0].channels,("BM25",))
        self.assertIsNone(retriever.encoder_id)

    def test_fused_ranking_with_injected_vectors(self):
        # Controlled, explicitly MOCKED vectors: verifies reciprocal-rank fusion,
        # not quality of actual pretrained semantic embeddings.
        def mock_encoder(texts):
            return [(1.,0.) if "fifty" in t or "2030" in t else (0.,1.) for t in texts]
        retriever=HybridRetriever(self.subs,encoder=mock_encoder,encoder_id="MOCK_TEST_ONLY")
        hits=retriever.search("fifty percent",k=3)
        self.assertEqual(hits[0].chunk.subsection,"C")
        self.assertIn("BM25",hits[0].channels)
        self.assertIn("EMBEDDING",hits[0].channels)

    def test_embedding_requires_model_provenance(self):
        with self.assertRaises(ValueError):
            HybridRetriever(self.subs,encoder=lambda xs: [(1.,)]*len(xs))
        self.assertAlmostEqual(cosine((1.,0.),(1.,0.)),1.)

    def test_exact_evidence_and_failure_modes(self):
        retriever=BM25LegalRetriever(self.subs)
        b=assemble_evidence("fifty percent retail sales","NM_COOP",
                            retriever,self.chunks,build_reference_graph(self.chunks),top_k=1)
        c=self.subs[1]
        start=TEXT.index("fifty percent")
        end=start+len("fifty percent")
        item=FieldEvidence("target_fraction","0.50",c.chunk_id,start,end,TEXT[start:end])
        results=validate_field_evidence(TEXT,b,[item])
        self.assertEqual(results[0].status,"EVIDENCE_MATCHED_NOT_ADJUDICATED")
        invalid=FieldEvidence("target_fraction","0.50",c.chunk_id,start,end,"forty percent")
        self.assertEqual(validate_field_evidence(TEXT,b,[invalid])[0].status,"REJECT")
        wrong=FieldEvidence("target_fraction","0.50","not-retrieved",start,end,TEXT[start:end])
        self.assertEqual(validate_field_evidence(TEXT,b,[wrong])[0].reason,"CHUNK_NOT_RETRIEVED")
        with self.assertRaisesRegex(ValueError,"digest mismatch"):
            validate_field_evidence(TEXT+"x",b,[item])

if __name__=="__main__":
    unittest.main()
