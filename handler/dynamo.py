from botocore.exceptions import ClientError
import boto3

from handler.models import EncryptedAnswers
from handler.logger import logger
from handler.utils import ServiceResponse
from http import HTTPStatus


class Dynamo:
    # Answers should be write-once only. Dynamo allows this with Conditional expressions on the hash and range keys.
    NO_OVERWRITE_CONDITION = "attribute_not_exists(hashKey) AND attribute_not_exists(contextId)"

    def __init__(self, dynamodb_prefix):
        self.table = boto3.resource("dynamodb").Table(f"{dynamodb_prefix}EncryptedAnswers")

    def get_item(self, hash_key, context_id):
        try:
            return self.table.get_item(Key={"hashKey": hash_key, "contextId": context_id}).get("Item", None)
        except ClientError as e:
            logger.exception(e.response["Error"]["Message"])
            return None

    def get_encrypted_answers(self, company_key, form_id, context_id):
        encrypted_answers_hash_key = f"{company_key}:{form_id}"
        dynamo_encrypted_answers = self.get_item(encrypted_answers_hash_key, context_id)

        if dynamo_encrypted_answers is None:
            logger.error(f"Unable to fetch answers for {encrypted_answers_hash_key} and context {context_id}")
            return ServiceResponse.error(HTTPStatus.NOT_FOUND, "Unable to fetch answers")

        encrypted_answers = EncryptedAnswers(dynamo_encrypted_answers)
        return ServiceResponse.ok(encrypted_answers)

    def put_encrypted_answers(self, encrypted_answers):
        encrypted_answers_dict = encrypted_answers.to_dict()
        try:
            response = self.table.put_item(Item=encrypted_answers_dict,
                                           ConditionExpression=Dynamo.NO_OVERWRITE_CONDITION)
            if not response:
                return ServiceResponse.error(HTTPStatus.NOT_FOUND, "No response received from dynamo")
            if not response["ResponseMetadata"] or response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                return ServiceResponse.error(HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to write item to database")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return ServiceResponse.error(HTTPStatus.BAD_REQUEST, "Answer already exists for this id")
            else:
                return ServiceResponse.error(HTTPStatus.INTERNAL_SERVER_ERROR, e.response["Error"]["Message"])
        return ServiceResponse.ok(dict(success=True))
