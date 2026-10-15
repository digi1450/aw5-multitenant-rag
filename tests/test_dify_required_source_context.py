"""Offline diagnostic fixtures for the candidate Dify Code 2."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


CODE_PATH = Path(__file__).resolve().parents[1] / "dify/code/required_source_context.py"
SPEC = importlib.util.spec_from_file_location("required_source_context", CODE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def candidate(rank, name="B.pdf", document_id="b", content=None):
    return {
        "content": content if content is not None else f"synthetic chunk {rank}",
        "metadata": {
            "document_name": name,
            "document_id": document_id,
            "segment_id": f"segment-{rank}",
            "dataset_id": "fixture-dataset",
            "position": rank,
            "child_chunks": [{"id": f"child-{rank}", "content": "fixture child"}],
        },
        "title": "fixture title",
    }


def registry(*sources):
    return [{"data": [
        {"document_name": name, "document_id": document_id}
        for name, document_id in sources
    ]}]


def ranks(output):
    return [item["metadata"]["position"] for item in output["result"]]


def report(output):
    return json.loads(output["selection_report"])


class RequiredSourceContextTests(unittest.TestCase):
    def test_all_preserves_top15_and_does_not_require_registry(self):
        items = [candidate(i) for i in range(1, 31)]
        before = copy.deepcopy(items)
        out = MODULE.main(items, "ALL", "", None)
        self.assertEqual(ranks(out), list(range(1, 16)))
        self.assertEqual(items, before)
        for old, new in zip(items, out["result"]):
            self.assertEqual(new["metadata"], old["metadata"])
            self.assertEqual(new["title"], old["title"])
            self.assertTrue(new["content"].endswith(old["content"]))
        self.assertEqual(report(out)["required_sources_present"], [])

    def test_required_rank1_preserves_top15(self):
        items = [candidate(i) for i in range(1, 31)]
        items[0] = candidate(1, "A.pdf", "a")
        out = MODULE.main(items, "SELECTED", "A.pdf", registry(("A.pdf", "a")))
        self.assertEqual(ranks(out), list(range(1, 16)))

    def test_required_rank17_and_rank30_are_retained(self):
        for required_rank in (17, 30):
            with self.subTest(required_rank=required_rank):
                items = [candidate(i) for i in range(1, 31)]
                items[required_rank - 1] = candidate(required_rank, "A.pdf", "a")
                out = MODULE.main(items, "SELECTED", "A.pdf", registry(("A.pdf", "a")))
                self.assertEqual(ranks(out), list(range(1, 15)) + [required_rank])
                self.assertEqual(report(out)["required_sources_present"], ["A.pdf"])

    def test_missing_source_is_not_invented(self):
        out = MODULE.main([candidate(i) for i in range(1, 31)], "SELECTED", "A.pdf", registry(("A.pdf", "a")))
        self.assertEqual(ranks(out), list(range(1, 16)))
        self.assertEqual(report(out)["required_sources_not_retrieved"], ["A.pdf"])
        self.assertEqual(report(out)["candidate_coverage"], "partial")

    def test_two_required_sources_and_repeated_names(self):
        items = [candidate(i, "C.pdf", "c") for i in range(1, 31)]
        items[16] = candidate(17, "A.pdf", "a")
        items[22] = candidate(23, "B.pdf", "b")
        out = MODULE.main(items, "SELECTED", "A.pdf,B.pdf,A.pdf", registry(("A.pdf", "a"), ("B.pdf", "b")))
        self.assertEqual(ranks(out), list(range(1, 14)) + [17, 23])
        self.assertEqual(report(out)["required_sources_present"], ["A.pdf", "B.pdf"])

    def test_other_chunks_from_required_source_can_fill_by_rank(self):
        items = [candidate(i) for i in range(1, 31)]
        items[0] = candidate(1, "A.pdf", "a")
        items[1] = candidate(2, "A.pdf", "a")
        out = MODULE.main(items, "SELECTED", "A.pdf", registry(("A.pdf", "a")))
        self.assertEqual(ranks(out), list(range(1, 16)))
        self.assertEqual(len(ranks(out)), len(set(ranks(out))))

    def test_invalid_items_do_not_change_relative_order(self):
        items = [None, "invalid", {"content": " "}, candidate(4), candidate(5, "A.pdf", "a")]
        out = MODULE.main(items, "SELECTED", "A.pdf", registry(("A.pdf", "a")))
        self.assertEqual(ranks(out), [4, 5])
        self.assertEqual(out["evidence_count"], 2)

    def test_name_only_candidate_does_not_satisfy_required_id(self):
        item = candidate(1, "A.pdf", "a")
        del item["metadata"]["document_id"]
        out = MODULE.main([item], "SELECTED", "A.pdf", registry(("A.pdf", "a")))
        self.assertEqual(out["evidence_count"], 1)
        self.assertEqual(report(out)["required_sources_not_retrieved"], ["A.pdf"])

    def test_duplicate_filename_uses_registry_id(self):
        items = [candidate(i) for i in range(1, 31)]
        items[0] = candidate(1, "A.pdf", "other-a")
        items[16] = candidate(17, "A.pdf", "requested-a")
        out = MODULE.main(items, "SELECTED", "A.pdf", registry(("A.pdf", "requested-a")))
        self.assertIn(17, ranks(out))
        self.assertEqual(report(out)["required_sources"][0]["document_id"], "requested-a")

    def test_ambiguous_or_unknown_registry_source_stops_context(self):
        for sources in (registry(("A.pdf", "a1"), ("A.pdf", "a2")), registry(("B.pdf", "b"))):
            out = MODULE.main([candidate(1)], "SELECTED", "A.pdf", sources)
            self.assertFalse(out["has_evidence"])
            self.assertEqual(report(out)["required_sources_unresolved"], ["A.pdf"])

    def test_overflow_uses_retrieval_rank_and_reports_omission(self):
        names = [f"D{i}.pdf" for i in range(1, 17)]
        items = [candidate(i, name, f"id-{i}") for i, name in enumerate(names, 1)]
        sources = registry(*[(name, f"id-{i}") for i, name in enumerate(names, 1)])
        out = MODULE.main(items, "SELECTED", ",".join(reversed(names)), sources)
        self.assertEqual(ranks(out), list(range(1, 16)))
        self.assertEqual(report(out)["required_sources_omitted_by_limit"], ["D16.pdf"])
        self.assertEqual(report(out)["required_sources_not_retrieved"], [])

    def test_unresolved_mode_does_not_pass_unexpected_results(self):
        out = MODULE.main([candidate(1)], "UNRESOLVED", "", None)
        self.assertEqual(out["result"], [])
        self.assertFalse(out["has_evidence"])

    def test_selected_empty_or_malformed_names_fail(self):
        for names in ("", " ", "A.pdf,", None):
            with self.subTest(names=names), self.assertRaises(ValueError):
                MODULE.main([candidate(1)], "SELECTED", names, registry(("A.pdf", "a")))

    def test_none_wrong_result_type_and_missing_metadata(self):
        self.assertEqual(MODULE.main(None, "ALL", "", None)["result"], [])
        with self.assertRaises(ValueError):
            MODULE.main({}, "ALL", "", None)
        for metadata in (None, "invalid", {}):
            item = {"content": "fixture content", "metadata": metadata}
            out = MODULE.main([item], "ALL", "", None)
            self.assertEqual(out["evidence_count"], 1)
            self.assertEqual(out["result"][0]["metadata"], metadata)

    def test_exact_names_flat_registry_and_repeated_registry_rows(self):
        name = "เอกสาร ทดสอบ.PDF"
        item = candidate(1, name, "a")
        rows = [{"document_name": name, "document_id": "a"}] * 2
        self.assertTrue(MODULE.main([item], "SELECTED", name, rows)["has_evidence"])
        out = MODULE.main([item], "SELECTED", name.lower(), rows)
        self.assertEqual(report(out)["required_sources_unresolved"], [name.lower()])

    def test_bad_mode_and_registry_shape_fail(self):
        with self.assertRaises(ValueError):
            MODULE.main([], "UNKNOWN", "", [])
        with self.assertRaises(ValueError):
            MODULE.main([], "SELECTED", "A.pdf", [{"data": "invalid"}])


if __name__ == "__main__":
    unittest.main()
