import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from asf.core.hashing import stable_hash
from asf.repair.repair_authorization import RepairAuthorizationReceipt, build_receipt, verify_receipt
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_replay import replay_repair


ROOT = Path(__file__).resolve().parents[1]


def doc_plan() -> RepairPlan:
    import json
    return RepairPlan.from_dict(json.loads((ROOT / "examples" / "repair_plans" / "documentation_alignment_repair_plan.json").read_text(encoding="utf-8")))


class RepairAuthorizationTests(unittest.TestCase):
    def test_authorization_receipt_binds_exact_repair_plan_hash(self):
        plan = doc_plan()
        receipt = build_receipt(plan, human_authorizer="James", allowed_paths=["docs"])
        self.assertEqual(receipt.repair_plan_hash, stable_hash(plan.as_dict()))

    def test_wrong_repair_plan_hash_fails(self):
        plan = doc_plan()
        receipt = build_receipt(plan, human_authorizer="James", allowed_paths=["docs"])
        receipt.repair_plan_hash = "wrong"
        self.assertIn("REPAIR_PLAN_HASH_MISMATCH", verify_receipt(receipt, plan)["failures"])

    def test_expired_authorization_fails(self):
        plan = doc_plan()
        expired = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        receipt = build_receipt(plan, human_authorizer="James", allowed_paths=["docs"], expires_at=expired)
        self.assertIn("AUTHORIZATION_EXPIRED", verify_receipt(receipt, plan)["failures"])

    def test_missing_human_authorizer_fails(self):
        plan = doc_plan()
        receipt = build_receipt(plan, human_authorizer="", allowed_paths=["docs"])
        self.assertIn("HUMAN_AUTHORIZER_MISSING", verify_receipt(receipt, plan)["failures"])

    def test_authorization_receipt_binds_replay_hash(self):
        plan = doc_plan()
        receipt = build_receipt(plan, human_authorizer="James", allowed_paths=["docs"])
        self.assertEqual(receipt.repair_replay_hash, stable_hash(replay_repair(plan).as_dict()))

    def test_authorization_rejects_wrong_repair_class(self):
        plan = doc_plan()
        receipt = build_receipt(plan, human_authorizer="James", allowed_paths=["docs"])
        receipt.allowed_repair_class = "policy_mismatch"
        self.assertIn("REPAIR_CLASS_NOT_AUTHORIZED", verify_receipt(receipt, plan)["failures"])

    def test_authorization_rejects_non_single_use(self):
        plan = doc_plan()
        receipt = build_receipt(plan, human_authorizer="James", allowed_paths=["docs"], single_use=False)
        self.assertIn("AUTHORIZATION_NOT_SINGLE_USE", verify_receipt(receipt, plan)["failures"])

    def test_authorization_rejects_unallowed_path(self):
        plan = doc_plan()
        receipt = build_receipt(plan, human_authorizer="James", allowed_paths=["docs"])
        self.assertIn("PATH_NOT_AUTHORIZED", verify_receipt(receipt, plan, target_path="README.md")["failures"])


if __name__ == "__main__":
    unittest.main()
