import hashlib
import hmac
import json
import unittest

from vendel_sdk.webhook import verify_webhook_signature


class TestVerifyWebhookSignature(unittest.TestCase):
    def _sign(self, payload, secret):
        if isinstance(payload, str):
            payload = payload.encode()
        return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    def test_valid_string_payload(self):
        payload = '{"event":"sms.sent"}'
        sig = self._sign(payload, "secret123")
        self.assertTrue(verify_webhook_signature(payload, sig, "secret123"))

    def test_invalid_signature(self):
        self.assertFalse(verify_webhook_signature("payload", "invalid", "secret"))

    def test_wrong_secret(self):
        payload = "test"
        sig = self._sign(payload, "correct_secret")
        self.assertFalse(verify_webhook_signature(payload, sig, "wrong_secret"))

    def test_dict_payload_sorted_keys(self):
        payload = {"z_key": "last", "a_key": "first"}
        serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        sig = self._sign(serialized, "secret")
        self.assertTrue(verify_webhook_signature(payload, sig, "secret"))

    def test_bytes_payload(self):
        payload = b'{"event":"test"}'
        sig = self._sign(payload, "secret")
        self.assertTrue(verify_webhook_signature(payload, sig, "secret"))


if __name__ == "__main__":
    unittest.main()
