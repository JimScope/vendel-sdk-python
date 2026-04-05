import unittest

from vendel_sdk.types import SendSMSResponse, Quota


class TestSendSMSResponse(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "batch_id": "b1", "message_ids": ["m1", "m2"],
            "recipients_count": 2, "status": "accepted",
        }
        resp = SendSMSResponse.from_dict(data)
        self.assertEqual(resp.batch_id, "b1")
        self.assertEqual(resp.message_ids, ["m1", "m2"])
        self.assertEqual(resp.recipients_count, 2)
        self.assertEqual(resp.status, "accepted")


class TestQuota(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "plan": "Pro", "sms_sent_this_month": 50,
            "max_sms_per_month": 1000, "devices_registered": 2,
            "max_devices": 5, "reset_date": "2026-05-01",
        }
        q = Quota.from_dict(data)
        self.assertEqual(q.plan, "Pro")
        self.assertEqual(q.max_sms_per_month, 1000)

    def test_from_dict_missing_reset_date(self):
        data = {
            "plan": "Free", "sms_sent_this_month": 0,
            "max_sms_per_month": 50, "devices_registered": 0,
            "max_devices": 1,
        }
        q = Quota.from_dict(data)
        self.assertEqual(q.reset_date, "")


if __name__ == "__main__":
    unittest.main()
