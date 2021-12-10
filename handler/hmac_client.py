import base64
import hashlib
import codecs
import hmac
import urllib.parse
import time

from handler.utils import UTF_8

HEADER_CONTENT_TYPE = "Content-Type"
MIME_TYPE_JSON = "application/json"

HEADER_SIGNATURE_V2 = "X-Auth-Signature-V2"
HEADER_API_KEY = "X-Auth-ApiKey"
HEADER_TIMESTAMP = "X-Auth-Timestamp"
HEADER_COMPANY_KEY = "X-SMM-COMPANY-KEY"

HEADER_IDENTITY = "X-SMM-IDENTITY"
SYSTEM_USER = '{"uuid":null,"email":null,"loginDisabled":null,"deleted":null,"profileImageUUID":null,' \
              '"description":null,"website":null,"title":null,"locale":null,"name":null,"companyID":null,' \
              '"teamId":null,"supervisorID":null,"roleNames":["admin"],"userId":{"entityType":"USER","rawId":0}}'


class HmacClient(object):
    def __init__(self, company_key, api_key, api_secret):
        self.company_key = company_key
        self.api_key = api_key
        self.api_secret = api_secret

    def get_base_headers(self, epoch_millis_timestamp):
        return {
            HEADER_API_KEY: self.api_key,
            HEADER_TIMESTAMP: epoch_millis_timestamp,
            HEADER_COMPANY_KEY: self.company_key,
            HEADER_IDENTITY: SYSTEM_USER,
            HEADER_CONTENT_TYPE: MIME_TYPE_JSON
        }

    def get_hmac_headers(self,
                         method,
                         uri,
                         request_body):

        epoch_millis_timestamp = str(int(round(time.time() * 1000)))
        header_output = self.get_base_headers(epoch_millis_timestamp)

        parsed_uri = urllib.parse.urlparse(uri)

        fingerprint_header_parts = f":x-smm-company-key:{self.company_key}:x-smm-identity:{SYSTEM_USER}"

        v2_uri = parsed_uri.hostname.lower()
        v2_uri += parsed_uri.path
        if parsed_uri.query:
            v2_uri += '?' + parsed_uri.query

        fingerprint = "|".join([epoch_millis_timestamp, method, v2_uri, request_body, fingerprint_header_parts])

        api_secret_bytes = codecs.encode(self.api_secret, encoding=UTF_8)
        fingerprint_bytes = codecs.encode(fingerprint)
        signature = hmac.new(api_secret_bytes, fingerprint_bytes, hashlib.sha256).digest()

        header_output[HEADER_SIGNATURE_V2] = base64.b64encode(signature)
        return header_output
