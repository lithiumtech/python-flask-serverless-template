from http import HTTPStatus
from uuid import uuid3, UUID

from handler.logger import logger
from handler.utils import base64_decode_uuid, ServiceResponse


# uuid3 expects a "namespace" component, we don't want to give it one.
class NullNamespace(UUID):
    bytes = b''


class SignatureService:
    def __init__(self, hmac_secret):
        self.hmac_secret = hmac_secret

    def verify(self, context_id, encoded_signature_uuid):
        try:
            signature_uuid = UUID(base64_decode_uuid(encoded_signature_uuid))
            generated_uuid = uuid3(NullNamespace, context_id + self.hmac_secret)

            if signature_uuid == generated_uuid:
                return ServiceResponse.ok()

            logger.warn(f"UUID: {context_id} does not match signature: {encoded_signature_uuid}")
        except Exception:
            logger.exception(f"Exception verifying uuid {context_id} for signature {encoded_signature_uuid}")

        return ServiceResponse.error(HTTPStatus.BAD_REQUEST, "Unable to verify signature")
