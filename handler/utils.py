import os
import time
import base64
import binascii

from http import HTTPStatus
from uuid import UUID

from handler.logger import logger

# todo perhaps a python module has this constant? Couldn't find one.
UTF_8 = "utf-8"


class ServiceResponse:
    def __init__(self, status, payload, error):
        self.status = status
        self.payload = payload
        self.error = error

    def is_ok(self):
        return self.status == HTTPStatus.OK and self.error is None

    def is_not_ok(self):
        return not self.is_ok()

    @staticmethod
    def ok(payload=None):
        return ServiceResponse(HTTPStatus.OK, payload, None)

    @staticmethod
    def error(status, error=None):
        if error is None:
            error = str(status.name)  # Error string should be the HTTPStatus enum name if not provided
        return ServiceResponse(status, None, error)


def base64_encode(string):
    encoded = base64.urlsafe_b64encode(string)
    return encoded.rstrip(b"=")


def base64_decode(string):
    if string is None:
        logger.error("Attempting to decode a null string")
        return None

    padding = 4 - (len(string) % 4)
    string = string + ("=" * padding)
    try:
        return base64.urlsafe_b64decode(string)
    except binascii.Error as e:
        logger.error(f"Unable to base64 decode string {string}, error {e}")
        return None


def base64_decode_uuid(encoded_uuid):
    try:
        return str(UUID(bytes=base64_decode(encoded_uuid)))
    except (TypeError, ValueError) as e:
        logger.error(f"Unable to decode UUID {encoded_uuid}, error {e}")
        return None


def base64_decode_company_key(encoded_company_key):
    if encoded_company_key is None:
        logger.warn("Attempting to decode null company key")
        return None

    try:
        decoded_company_key = base64_decode(encoded_company_key)
        company_key = decoded_company_key.decode(UTF_8)

        return company_key if company_key else None
    except binascii.Error as e:
        logger.error(f"Unable to decode company key {encoded_company_key}, error: {e}")
        return None


def any_invalid_uuids(*args):
    for value in args:
        try:
            UUID(value, version=4)
        except ValueError:
            return True
    return False


def current_seconds():
    return round(time.time())


# This returns the current seconds and ttl in a tuple. For tests we want to know which EXACT current_ts was used.
def get_current_and_ttl_seconds(ttl_seconds):
    current_ts_seconds = current_seconds()
    ttl_ts_seconds = round(current_ts_seconds + ttl_seconds)
    return current_ts_seconds, ttl_ts_seconds


def clean_url_param(param):
    # some url params need to be utf8 encoded ('+' -> '%2b')
    # make sure that + char that may have been decoded (into a space) is not decoded
    if param:
        return param.replace(' ', '+')
    return param


def is_local():
    return os.environ.get("AWS_EXECUTION_ENV") is None
