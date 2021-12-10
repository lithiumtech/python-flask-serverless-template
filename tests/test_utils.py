import unittest
from http import HTTPStatus

from handler.utils import ServiceResponse, any_invalid_uuids, get_current_and_ttl_seconds

ZERO_UUID = "00000000-0000-0000-0000-000000000000"
SOME_UUID = "abcdef01-0000-0000-0000-000000000000"


class UtilsTest(unittest.TestCase):

    def test_service_response(self):
        ok_response = ServiceResponse.ok({"key": "value"})
        error_response = ServiceResponse.error(HTTPStatus.NOT_FOUND, "Not found")

        self.assertTrue(ok_response.is_ok())
        self.assertTrue(error_response.is_not_ok())
        self.assertEqual(ok_response.payload["key"], "value")
        self.assertEqual(error_response.error, "Not found")

    def test_any_invalid_uuids(self):
        self.assertFalse(any_invalid_uuids(ZERO_UUID, SOME_UUID))
        self.assertTrue(any_invalid_uuids(ZERO_UUID, "not a uuid"))

    def test_get_current_and_ttl_seconds(self):
        current, specific_ttl = get_current_and_ttl_seconds(5)  # 5 seconds
        self.assertEqual(specific_ttl, current + 5)
