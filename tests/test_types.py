import unittest

from vendel_sdk.types import Device, MessageStatus, Quota, SendSMSResponse


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


class TestDevice(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "id": "dev1",
            "name": "Pixel 8",
            "device_type": "android",
            "phone_number": "+15551234567",
            "created": "2026-04-01",
            "updated": "2026-04-02",
        }
        d = Device.from_dict(data)
        self.assertEqual(d.id, "dev1")
        self.assertEqual(d.name, "Pixel 8")
        self.assertEqual(d.device_type, "android")
        self.assertEqual(d.phone_number, "+15551234567")

    def test_from_dict_defaults(self):
        d = Device.from_dict({})
        self.assertEqual(d.id, "")
        self.assertEqual(d.device_type, "")


class TestMessageStatusNewFields(unittest.TestCase):
    def test_from_dict_with_new_fields(self):
        data = {
            "id": "m1", "batch_id": "b1", "recipient": "+1",
            "from_number": "+2", "body": "hi",
            "status": "sent", "message_type": "outbound",
            "error_message": "", "device_id": "dev1",
            "sent_at": "t1", "delivered_at": "t2",
            "created": "c", "updated": "u",
        }
        m = MessageStatus.from_dict(data)
        self.assertEqual(m.from_number, "+2")
        self.assertEqual(m.message_type, "outbound")
        self.assertEqual(m.body, "hi")
        self.assertEqual(m.sent_at, "t1")
        self.assertEqual(m.delivered_at, "t2")

    def test_from_dict_legacy_payload(self):
        # Backwards-compatible: payloads without the new fields still parse.
        data = {
            "id": "m1", "batch_id": "b1", "recipient": "+1",
            "status": "sent", "error_message": "", "device_id": "dev1",
            "created": "c", "updated": "u",
        }
        m = MessageStatus.from_dict(data)
        self.assertEqual(m.from_number, "")
        self.assertEqual(m.message_type, "")
        self.assertEqual(m.body, "")


if __name__ == "__main__":
    unittest.main()
