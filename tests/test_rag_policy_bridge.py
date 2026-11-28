import unittest
from dataclasses import replace
from energy_policy_llm.legal_chunker import chunk_legal_text
from energy_policy_llm.reference_graph import build_reference_graph
from energy_policy_llm.retrievers import BM25LegalRetriever
from energy_policy_llm.evidence_bundle import assemble_evidence
from energy_policy_llm.field_evidence import FieldEvidence
from energy_policy_llm.rag_policy_bridge import ProposedPolicyFields,validate_proposed_policy
from energy_policy_llm.compiler_v2 import compile_policy
from energy_policy_llm.model_profile import synthetic_profile

TEXT="""17.9.571.8 RENEWABLE PORTFOLIO:
        C. By 2030, fifty percent of New Mexico retail sales must be renewable.
17.9.571.11 CERTIFICATES:
        D. WREGIS rules refer to 17.9.571.13(E).
17.9.571.13 REPORTS:
        A. Annual report due April 30.
"""
class RagToIrTests(unittest.TestCase):
    def setUp(self):
        self.chunks=chunk_legal_text(TEXT,"NM")
        subs=[c for c in self.chunks if c.subsection]
        r=BM25LegalRetriever(subs)
        self.bundle=assemble_evidence("fifty percent retail sales","NM",r,self.chunks,
                                      build_reference_graph(self.chunks),top_k=1)
        self.sub=next(c for c in subs if c.provision=="17.9.571.8")
        def cite(field,phrase):
            start=TEXT.index(phrase,self.sub.start_char,self.sub.end_char)
            return FieldEvidence(field,"proposed value",self.sub.chunk_id,start,
                                 start+len(phrase),phrase)
        self.citations=(
            cite("legal_type","must be renewable"),
            cite("metric","retail sales"),
            cite("entity_id","New Mexico"),
            cite("year","2030"),
            cite("target_fraction","fifty percent"))
        self.draft=ProposedPolicyFields("AI-2030","17.9.571.8","TARGET",
                       "ELIGIBLE_RENEWABLE_RETAIL_SALES",
                       "distribution_cooperative",2030,.5,
                       field_evidence=self.citations)

    def test_valid_evidence_not_gold_and_compiler_abstains(self):
        result=validate_proposed_policy(TEXT,self.bundle,self.draft)
        self.assertEqual(result.status,"EVIDENCE_MATCHED_AI_DRAFT_NEEDS_SEMANTIC_REVIEW")
        self.assertFalse(result.human_gold)
        self.assertFalse(result.policy_ir.evidence_verified)
        self.assertFalse(result.policy_ir.human_adjudicated)
        out=compile_policy(result.policy_ir,synthetic_profile(full=True))
        self.assertEqual(out.status,"ABSTAIN")

    def test_missing_field_and_bad_quote(self):
        missing=replace(self.draft,field_evidence=self.citations[:-1])
        self.assertEqual(validate_proposed_policy(TEXT,self.bundle,missing).status,"ABSTAIN")
        incorrect=replace(self.citations[-1],exact_text="sixty percent")
        altered=replace(self.draft,field_evidence=(*self.citations[:-1],incorrect))
        self.assertIn("QUOTE_MISMATCH",str(validate_proposed_policy(TEXT,self.bundle,altered).reasons))

    def test_no_unverified_provision(self):
        c=replace(self.draft,provision="17.9.571.99")
        self.assertIn("PROVISION_NOT_IN_EVIDENCE_BUNDLE",
                     validate_proposed_policy(TEXT,self.bundle,c).reasons)

    def test_unknown_controlled_label(self):
        c=replace(self.draft,metric="GENERATION_AS_RETAIL_SALES")
        self.assertEqual(validate_proposed_policy(TEXT,self.bundle,c).status,"ABSTAIN")

    def test_wrong_source_sha(self):
        result=validate_proposed_policy(TEXT+"X",self.bundle,self.draft)
        self.assertEqual(result.status,"ABSTAIN")
        self.assertIn("SOURCE_INTEGRITY",str(result.reasons))

if __name__=="__main__":
    unittest.main()
