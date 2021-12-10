import boto3
from botocore.exceptions import ClientError

from handler.logger import logger

SECRET_PATH_FORMAT = "/{universe}/{region}/live/service-name/{secret_path}"


class SecretsManager:
    def __init__(self, universe="qa", region="us-west-2"):
        self.universe = universe
        self.region = region
        self.client = boto3.client('secretsmanager')

    def get_secret_by_path(self, *path_components):
        secret_path = "/".join(path_components)
        secret_id = SECRET_PATH_FORMAT.format(universe=self.universe, region=self.region, secret_path=secret_path)
        try:
            secret_response = self.client.get_secret_value(SecretId=secret_id)
            if secret_response and secret_response['SecretString'] is not None:
                return secret_response['SecretString']
            return None
        except ClientError:
            # if e.response['Error']['Code'] == 'DecryptionFailureException':
            logger.exception("Something wrong happened with AWS SecretsManager while retrieving secret %s. Error = %s", secret_id)
            return None
