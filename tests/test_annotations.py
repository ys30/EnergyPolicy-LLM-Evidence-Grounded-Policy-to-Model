import unittest
from dataclasses import replace
from hashlib import sha256
from energy_policy_llm.annotations import EvidenceSpan, gold_ready


TEXT = "Section 1: a hypothetical 50% by 2030 rule."
HASH = sha256(TEXT.encode("utf-8")).hexdigest()
START = TEXT.index("50%")
END = START + len("50% by 2030")


def candidate(**overrides):
    fields = dict(document_id="synthetic", snapshot_sha256=HASH, start_char=START,
                  end_char=END, quote="50% by 2030", source_version="synthetic-v1")
    fields.update(overrides)
    return EvidenceSpan(**fields)


class AnnotationTests(unittest.TestCase):
    def test_candidate_not_gold(self):
        self.assertFalse(gold_ready(candidate(), TEXT))

    def test_two_annotators_and_adjudication(self):
        s = candidate(decision="adjudicated", annotator_1="reviewer-a",
                      annotator_2="reviewer-b", adjudicator="reviewer-c")
        self.assertTrue(gold_ready(s, TEXT))

    def test_quoting_error_fails(self):
        with self.assertRaises(ValueError):
            gold_ready(candidate(quote="60% by 2030"), TEXT)

    def test_hash_change_fails(self):
        with self.assertRaises(ValueError):
            gold_ready(candidate(snapshot_sha256="bad"), TEXT)

    def test_bad_offsets_fail(self):
        with self.assertRaises(ValueError):
            gold_ready(candidate(end_char=999), TEXT)

    def test_unreviewed_cannot_claim_gold(self):
        with self.assertRaises(ValueError):
            gold_ready(candidate(decision="adjudicated"), TEXT)

    def test_reviewers_must_be_distinct(self):
        with self.assertRaises(ValueError):
            gold_ready(candidate(decision="adjudicated", annotator_1="same",
                                 annotator_2="same", adjudicator="third"), TEXT)


if __name__ == "__main__":
    unittest.main()
