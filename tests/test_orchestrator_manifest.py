"""Approval and graph validation must fail before any Git or model side effect."""
import copy
import unittest

from socrates_orchestrator.manifest import ManifestError, strict_json, validate
from socrates_orchestrator.protocol import validate_result


def example():
    return {
        "schema_version": 1, "run_id": "demo", "goal": "A working joint feature",
        "parent_brief": ".agent/TASK_BRIEF.md", "milestones": ["Delegate", "Integrate"],
        "criteria": [{"id": "C1", "text": "Backend works"}, {"id": "C2", "text": "Joint behavior works"}],
        "parent_criteria": ["C2"],
        "tasks": [{"id": "backend", "title": "Backend", "instructions": "Implement the contract",
                   "milestones": ["Build backend"], "criteria": ["C1"], "depends_on": [],
                   "reviewer": "parent", "allowed_paths": ["src/"], "verify": []}],
        "integration_verify": [["python3", "-m", "unittest"]],
        "authorization": {"parent_plan_approved": True, "delegate_plan_review": True,
                          "delegate_result_review": True, "local_merge": True, "final_reviewer": "human"},
    }


class ManifestTests(unittest.TestCase):
    def test_valid_graph_preserves_original_criteria_and_explicit_authorities(self):
        source = example()
        result = validate(source)
        self.assertEqual(result["criteria"], source["criteria"])
        self.assertEqual(result["parent_criteria"], ["C2"])
        self.assertEqual(result["repair_mode"], "resume")
        self.assertNotIn("max_workers", source)

    def test_unsafe_graphs_and_unapproved_operations_are_rejected(self):
        def change_authority(m):
            m["authorization"]["local_merge"] = False

        mutations = [
            change_authority,
            lambda m: m["authorization"].update(final_reviewer="parent"),
            lambda m: m["parent_criteria"].clear(),
            lambda m: m["tasks"][0].update(depends_on=["missing"]),
            lambda m: m["tasks"][0].update(depends_on=["backend"]),
            lambda m: m["tasks"][0].update(allowed_paths=["../outside/"]),
            lambda m: m["tasks"][0].update(allowed_paths=[".git/config"]),
            lambda m: m["tasks"][0].update(criteria=["unapproved"]),
            lambda m: m["tasks"][0].update(id="parent"),
            lambda m: m["tasks"][0].update(reviewer="self"),
            lambda m: m["tasks"][0].update(verify=["shell command"]),
            lambda m: m.update(max_workers=True),
            lambda m: m.update(schema_version=True),
            lambda m: m.update(unrecognized="ignored authority?"),
        ]
        for number, mutation in enumerate(mutations):
            with self.subTest(number=number):
                source = example()
                mutation(source)
                with self.assertRaises(ManifestError):
                    validate(source)

    def test_cycle_with_multiple_nodes_and_duplicate_identifiers(self):
        source = example()
        second = copy.deepcopy(source["tasks"][0])
        second.update(id="ui", depends_on=["backend"])
        source["tasks"].append(second)
        source["tasks"][0]["depends_on"] = ["ui"]
        with self.assertRaisesRegex(ManifestError, "cycle"):
            validate(source)
        source["tasks"][0]["depends_on"] = []
        self.assertEqual(len(validate(source)["tasks"]), 2)
        second["id"] = "backend"
        with self.assertRaisesRegex(ManifestError, "Duplicate"):
            validate(source)

    def test_ambiguous_json_is_not_accepted(self):
        for text in ('{"authority": true, "authority": false}', '{"value": NaN}', '{"value": Infinity}'):
            with self.subTest(text=text), self.assertRaises(ManifestError):
                strict_json(text)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.request = {"task_id": "backend", "operation": "review_result", "invocation_id": "attempt-1",
                        "candidate_id": "candidate-1", "policy_hash": "same-policy", "criterion_ids": ["C1"]}
        self.result = {key: self.request[key] for key in self.request if key != "criterion_ids"}
        self.result.update(kind="approved", notes="Observable outcome checked",
                           criteria=[{"id": "C1", "status": "passed", "evidence": "Executed the required contract test"}])

    def test_approval_is_bound_to_exact_task_attempt_candidate_and_policy(self):
        self.assertEqual(validate_result(self.result, self.request, {"approved"}), self.result)
        for field in ("task_id", "operation", "invocation_id", "candidate_id", "policy_hash"):
            with self.subTest(field=field):
                altered = copy.deepcopy(self.result)
                altered[field] = "another-identity"
                with self.assertRaises(ValueError):
                    validate_result(altered, self.request, {"approved"})

    def test_approval_cannot_omit_fail_or_duplicate_criteria(self):
        evidence_cases = [[], self.result["criteria"] * 2,
                          [{"id": "C1", "status": "not_checked", "evidence": "No run"}],
                          [{"id": "C1", "status": "failed", "evidence": "Observed failure"}],
                          [{"id": "C2", "status": "passed", "evidence": "Different scope"}]]
        for evidence in evidence_cases:
            with self.subTest(evidence=evidence):
                altered = {**self.result, "criteria": evidence}
                with self.assertRaises(ValueError):
                    validate_result(altered, self.request, {"approved"})


if __name__ == "__main__":
    unittest.main()
