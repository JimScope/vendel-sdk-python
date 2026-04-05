import unittest

from vendel_sdk.exceptions import VendelError, VendelAPIError, VendelQuotaError


class TestExceptions(unittest.TestCase):
    def test_api_error_str(self):
        err = VendelAPIError(400, "Bad request")
        self.assertEqual(str(err), "[400] Bad request")
        self.assertEqual(err.status_code, 400)
        self.assertEqual(err.detail, {})

    def test_api_error_with_detail(self):
        err = VendelAPIError(422, "Validation failed", {"field": "body"})
        self.assertEqual(err.detail, {"field": "body"})

    def test_api_error_inherits_vendel_error(self):
        err = VendelAPIError(500, "Server error")
        self.assertIsInstance(err, VendelError)
        self.assertIsInstance(err, Exception)

    def test_quota_error_inherits(self):
        err = VendelQuotaError("Quota exceeded", {
            "limit": 100, "used": 100, "available": 0,
        })
        self.assertIsInstance(err, VendelAPIError)
        self.assertIsInstance(err, VendelError)
        self.assertEqual(err.status_code, 429)

    def test_quota_error_fields(self):
        err = VendelQuotaError("Exceeded", {
            "limit": 500, "used": 500, "available": 0,
        })
        self.assertEqual(err.limit, 500)
        self.assertEqual(err.used, 500)
        self.assertEqual(err.available, 0)

    def test_quota_error_default_fields(self):
        err = VendelQuotaError("Exceeded", {})
        self.assertEqual(err.limit, 0)
        self.assertEqual(err.used, 0)
        self.assertEqual(err.available, 0)


if __name__ == "__main__":
    unittest.main()
