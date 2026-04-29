import unittest
from unittest.mock import patch, MagicMock

from vendel_sdk.client import VendelClient
from vendel_sdk.exceptions import VendelAPIError, VendelQuotaError


class TestClientInit(unittest.TestCase):
    def test_strips_trailing_slash(self):
        client = VendelClient("https://api.example.com/", "vk_test")
        self.assertEqual(client.base_url, "https://api.example.com")

    def test_sets_api_key_header(self):
        client = VendelClient("https://api.example.com", "vk_key_123")
        self.assertEqual(client._session.headers["X-API-Key"], "vk_key_123")


class TestSendSms(unittest.TestCase):
    def setUp(self):
        self.client = VendelClient("https://api.example.com", "vk_test")

    @patch.object(VendelClient, "_post")
    def test_success(self, mock_post):
        mock_post.return_value = {
            "batch_id": "b1", "message_ids": ["m1"],
            "recipients_count": 1, "status": "accepted",
        }
        resp = self.client.send_sms(["+1234567890"], "Hello")
        mock_post.assert_called_once_with(
            "/api/sms/send",
            {"recipients": ["+1234567890"], "body": "Hello"},
        )
        self.assertEqual(resp.batch_id, "b1")
        self.assertEqual(resp.status, "accepted")

    @patch.object(VendelClient, "_post")
    def test_with_device_id(self, mock_post):
        mock_post.return_value = {
            "batch_id": "", "message_ids": ["m1"],
            "recipients_count": 1, "status": "accepted",
        }
        self.client.send_sms(["+1"], "Hi", device_id="dev1")
        payload = mock_post.call_args[0][1]
        self.assertEqual(payload["device_id"], "dev1")

    @patch.object(VendelClient, "_post")
    def test_with_group_ids(self, mock_post):
        mock_post.return_value = {
            "batch_id": "", "message_ids": ["m1"],
            "recipients_count": 5, "status": "accepted",
        }
        self.client.send_sms([], "Hi", group_ids=["g1", "g2"])
        payload = mock_post.call_args[0][1]
        self.assertEqual(payload["group_ids"], ["g1", "g2"])

    @patch.object(VendelClient, "_post")
    def test_no_group_ids_when_none(self, mock_post):
        mock_post.return_value = {
            "batch_id": "", "message_ids": ["m1"],
            "recipients_count": 1, "status": "accepted",
        }
        self.client.send_sms(["+1"], "Hi")
        payload = mock_post.call_args[0][1]
        self.assertNotIn("group_ids", payload)


class TestSendSmsTemplate(unittest.TestCase):
    def setUp(self):
        self.client = VendelClient("https://api.example.com", "vk_test")

    @patch.object(VendelClient, "_post")
    def test_success(self, mock_post):
        mock_post.return_value = {
            "batch_id": "b1", "message_ids": ["m1"],
            "recipients_count": 1, "status": "accepted",
        }
        resp = self.client.send_sms_template(
            ["+1"], "tmpl_1", variables={"code": "1234"},
        )
        args = mock_post.call_args[0]
        self.assertEqual(args[0], "/api/sms/send-template")
        self.assertEqual(args[1]["template_id"], "tmpl_1")
        self.assertEqual(args[1]["variables"], {"code": "1234"})

    @patch.object(VendelClient, "_post")
    def test_with_group_ids(self, mock_post):
        mock_post.return_value = {
            "batch_id": "", "message_ids": ["m1"],
            "recipients_count": 5, "status": "accepted",
        }
        self.client.send_sms_template([], "tmpl_1", group_ids=["g1"])
        payload = mock_post.call_args[0][1]
        self.assertEqual(payload["group_ids"], ["g1"])


class TestGetQuota(unittest.TestCase):
    @patch.object(VendelClient, "_get")
    def test_success(self, mock_get):
        mock_get.return_value = {
            "plan": "Pro", "sms_sent_this_month": 50,
            "max_sms_per_month": 1000, "devices_registered": 2,
            "max_devices": 5, "reset_date": "2026-05-01",
        }
        client = VendelClient("https://api.example.com", "vk_test")
        quota = client.get_quota()
        mock_get.assert_called_once_with("/api/plans/quota")
        self.assertEqual(quota.plan, "Pro")
        self.assertEqual(quota.sms_sent_this_month, 50)


class TestListDevices(unittest.TestCase):
    def setUp(self):
        self.client = VendelClient("https://api.example.com", "vk_test")

    @patch.object(VendelClient, "_get")
    def test_success(self, mock_get):
        mock_get.return_value = {
            "items": [
                {
                    "id": "dev1", "name": "Pixel", "device_type": "android",
                    "phone_number": "+15551234567",
                    "created": "2026-04-01", "updated": "2026-04-02",
                },
            ],
            "page": 1, "per_page": 50, "total_items": 1, "total_pages": 1,
        }
        resp = self.client.list_devices()
        mock_get.assert_called_once_with(
            "/api/devices",
            params={"page": 1, "per_page": 50, "device_type": None},
        )
        self.assertEqual(len(resp.items), 1)
        self.assertEqual(resp.items[0].id, "dev1")
        self.assertEqual(resp.items[0].device_type, "android")

    @patch.object(VendelClient, "_get")
    def test_with_filter(self, mock_get):
        mock_get.return_value = {
            "items": [], "page": 2, "per_page": 10,
            "total_items": 0, "total_pages": 0,
        }
        self.client.list_devices(page=2, per_page=10, device_type="android")
        mock_get.assert_called_once_with(
            "/api/devices",
            params={"page": 2, "per_page": 10, "device_type": "android"},
        )


class TestListMessages(unittest.TestCase):
    def setUp(self):
        self.client = VendelClient("https://api.example.com", "vk_test")

    @patch.object(VendelClient, "_get")
    def test_success(self, mock_get):
        mock_get.return_value = {
            "items": [
                {
                    "id": "m1", "batch_id": "b1", "recipient": "+15551234567",
                    "from_number": "+15557654321", "body": "Hello",
                    "status": "sent", "message_type": "outbound",
                    "error_message": "", "device_id": "dev1",
                    "sent_at": "2026-04-29T10:00:00Z",
                    "delivered_at": "2026-04-29T10:00:05Z",
                    "created": "2026-04-29T10:00:00Z",
                    "updated": "2026-04-29T10:00:05Z",
                },
            ],
            "page": 1, "per_page": 50, "total_items": 1, "total_pages": 1,
        }
        resp = self.client.list_messages()
        mock_get.assert_called_once_with(
            "/api/sms/messages",
            params={
                "page": 1, "per_page": 50, "status": None,
                "device_id": None, "batch_id": None, "recipient": None,
                "from": None, "to": None,
            },
        )
        self.assertEqual(len(resp.items), 1)
        self.assertEqual(resp.items[0].id, "m1")
        self.assertEqual(resp.items[0].from_number, "+15557654321")
        self.assertEqual(resp.items[0].message_type, "outbound")
        self.assertEqual(resp.items[0].body, "Hello")

    @patch.object(VendelClient, "_get")
    def test_maps_from_and_to(self, mock_get):
        mock_get.return_value = {
            "items": [], "page": 1, "per_page": 50,
            "total_items": 0, "total_pages": 0,
        }
        self.client.list_messages(
            status="failed",
            device_id="dev1",
            from_date="2026-04-01",
            to_date="2026-04-30",
        )
        mock_get.assert_called_once_with(
            "/api/sms/messages",
            params={
                "page": 1, "per_page": 50, "status": "failed",
                "device_id": "dev1", "batch_id": None, "recipient": None,
                "from": "2026-04-01", "to": "2026-04-30",
            },
        )


class TestGetParamsHandling(unittest.TestCase):
    def test_drops_none_params(self):
        client = VendelClient("https://api.example.com", "vk_test")
        with patch.object(client._session, "get") as mock_session_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.ok = True
            mock_resp.json.return_value = {
                "items": [], "page": 1, "per_page": 50,
                "total_items": 0, "total_pages": 0,
            }
            mock_session_get.return_value = mock_resp
            client._get(
                "/api/devices",
                params={"page": 1, "per_page": 50, "device_type": None},
            )
            kwargs = mock_session_get.call_args.kwargs
            self.assertEqual(kwargs["params"], {"page": 1, "per_page": 50})
            self.assertNotIn("device_type", kwargs["params"])

    def test_no_params_kwarg_when_none(self):
        client = VendelClient("https://api.example.com", "vk_test")
        with patch.object(client._session, "get") as mock_session_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.ok = True
            mock_resp.json.return_value = {}
            mock_session_get.return_value = mock_resp
            client._get("/api/plans/quota")
            kwargs = mock_session_get.call_args.kwargs
            self.assertIsNone(kwargs["params"])


class TestErrorHandling(unittest.TestCase):
    def test_api_error(self):
        resp = MagicMock()
        resp.status_code = 400
        resp.ok = False
        resp.json.return_value = {"message": "Bad request"}
        resp.reason = "Bad Request"
        with self.assertRaises(VendelAPIError) as ctx:
            VendelClient._handle_response(resp)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_quota_error(self):
        resp = MagicMock()
        resp.status_code = 429
        resp.ok = False
        resp.json.return_value = {
            "detail": "Quota exceeded",
            "limit": 100, "used": 100, "available": 0,
        }
        with self.assertRaises(VendelQuotaError) as ctx:
            VendelClient._handle_response(resp)
        self.assertEqual(ctx.exception.limit, 100)
        self.assertEqual(ctx.exception.available, 0)


if __name__ == "__main__":
    unittest.main()
