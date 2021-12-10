import json
import requests
from http import HTTPStatus

from handler.hmac_client import HmacClient
from handler.logger import logger
from handler.utils import base64_decode_company_key, ServiceResponse


class MLProcessorService:
    def __init__(self, api_endpoint, api_key, api_secret):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.api_secret = api_secret

    def get_form_context(self, company_key, context_id):
        hmac_client = HmacClient(company_key=company_key, api_key=self.api_key, api_secret=self.api_secret)
        rest_endpoint = f"{self.api_endpoint}/api/secure_forms/forms/formContext/{context_id}"
        headers = hmac_client.get_hmac_headers(method='GET',
                                               uri=rest_endpoint,
                                               request_body="")
        try:
            req = requests.get(rest_endpoint, headers=headers, timeout=10)
            if req.ok:
                result = json.loads(req.text)
                payload = result.get("payload", [])
                if payload:
                    return ServiceResponse.ok(dict(formContext=payload))
            logger.error(f"Failed to get form context by id {context_id} for company {company_key} with error: {req.status_code} {req.reason} {req.text}")
            return ServiceResponse.error(HTTPStatus.NOT_FOUND, "Failed to get form context")
        except requests.exceptions.RequestException:
            logger.exception(f"Something went wrong getting form context for company {company_key}")
            return ServiceResponse.error(HTTPStatus.INTERNAL_SERVER_ERROR, "Error getting form context")

    def save_form_response(self, encoded_company_key, context_id, plaintext_answers):
        if plaintext_answers is None:
            return ServiceResponse.error(HTTPStatus.BAD_REQUEST, "No plaintext answers provided")

        data = dict(answers=plaintext_answers)

        company_key = base64_decode_company_key(encoded_company_key)
        if company_key is None:
            return ServiceResponse.error(HTTPStatus.BAD_REQUEST, "Could not decode company key")

        hmac_client = HmacClient(company_key=company_key, api_key=self.api_key, api_secret=self.api_secret)
        rest_endpoint = f"{self.api_endpoint}/api/secure_forms/forms/saveFormResponse/{context_id}"

        headers = hmac_client.get_hmac_headers(method='PUT',
                                               uri=rest_endpoint,
                                               request_body=json.dumps(data))
        try:
            req = requests.put(rest_endpoint, json.dumps(data), headers=headers, timeout=10)
            if req.ok:
                return ServiceResponse.ok()
            logger.error(f"Failed to post form response {data} with error: {req.status_code} {req.reason} {req.text}")
            return ServiceResponse.error(HTTPStatus.NOT_FOUND, "Failed to get form context")
        except requests.exceptions.RequestException:
            logger.exception(f"Something went wrong posting form response {data}")
            return ServiceResponse.error(HTTPStatus.INTERNAL_SERVER_ERROR, "Error posting form response")
