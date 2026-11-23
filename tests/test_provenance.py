import unittest
from copy import deepcopy
from energy_policy_llm.provenance import validate_anchor_catalog

DATA = {
 "schema_version":"0.6.0",
 "primary_sources":[{"id":"S","url":"https://www.srca.nm.gov/parts/title17/17.009.0572.html","effective_date":"2023-02-28"}],
 "anchors":[{"anchor_id":"A","source_id":"S","provision":"17.9.572.10(B)(4)",
             "paraphrase":"Synthetic description","evidence_status":"source_section_located",
             "gold_status":"not_adjudicated"}]
}

class ProvenanceTests(unittest.TestCase):
    def test_catalog_valid(self):
        self.assertEqual(validate_anchor_catalog(DATA)["adjudicated_gold"], 0)

    def test_no_gold_promotion(self):
        d=deepcopy(DATA)
        d["anchors"][0]["gold_status"]="adjudicated"
        with self.assertRaises(ValueError): validate_anchor_catalog(d)

    def test_source_must_exist(self):
        d=deepcopy(DATA)
        d["anchors"][0]["source_id"]="unknown"
        with self.assertRaises(ValueError): validate_anchor_catalog(d)

    def test_no_duplicate_anchor(self):
        d=deepcopy(DATA)
        d["anchors"].append(deepcopy(d["anchors"][0]))
        with self.assertRaises(ValueError): validate_anchor_catalog(d)

    def test_nonofficial_domain_rejected(self):
        d=deepcopy(DATA)
        d["primary_sources"][0]["url"]="https://evil.example/path"
        with self.assertRaises(ValueError): validate_anchor_catalog(d)

if __name__ == "__main__":
    unittest.main()
