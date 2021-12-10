import os
from http import HTTPStatus

import jinja2
from flask import Flask, render_template, json

from handler.dynamo import Dynamo
from handler.logger import logger
from handler.secrets_manager import SecretsManager
from handler.service.mlprocessor_service import MLProcessorService
from handler.service.render_args_service import RenderArgsService
from handler.service.signature_service import SignatureService
from handler.utils import is_local

# Environment variables
REQUIRED_ENV = ["DYNAMO_DB_PREFIX", "UNIVERSE", "REGION"]
for env_var in REQUIRED_ENV:
    if env_var not in os.environ:
        raise Exception(f"Environment variable ${env_var} required")

UNIVERSE = os.environ["UNIVERSE"]
REGION = os.environ["REGION"]

# --- init Flask ---
app = Flask(__name__)

jinja2.Environment(
    loader=jinja2.PackageLoader(__name__),
    autoescape=jinja2.select_autoescape(["html"])
)

dynamodb_prefix = os.environ["DYNAMO_DB_PREFIX"]

developer_secrets_override = json.load(open("handler/_qa_developer_secrets.json"))
# Get these in the Global scope so that they are "cached" for the lifetime of the Lambda VM
mlprocessor_api = developer_secrets_override
if not is_local():
    secrets_manager = SecretsManager(UNIVERSE, REGION)
    mlprocessor_api = json.loads(secrets_manager.get_secret_by_path("api/ml-processor"))

mlprocessor_api_endpoint = mlprocessor_api["apiEndpoint"]
mlprocessor_api_key = mlprocessor_api["apiKey"]
mlprocessor_api_secret = mlprocessor_api["apiSecret"]

if not(mlprocessor_api_endpoint and mlprocessor_api_key and mlprocessor_api_secret):
    raise Exception("MLProcessor api credentials required")


# Crude "dependency injection" here by simply ordering the constructors.
# Once we have more than a handful of services, we should design this better.
dynamo = Dynamo(dynamodb_prefix)
signature_service = SignatureService(mlprocessor_api_secret)
mlprocessor_service = MLProcessorService(mlprocessor_api_endpoint, mlprocessor_api_key, mlprocessor_api_secret)
render_args_service = RenderArgsService(mlprocessor_service, signature_service)


# TODO CARE-3473: This endpoint should return a pretty Error page instead of a JSON error if something goes wrong
@app.route("/your/api/<path_param>/<other_path_param>", methods=["GET"])
def render_secure_form(path_param, other_path_param):
    logger.info(f"Path param {path_param} and other one {other_path_param}")
    return render_template("webview.html", title="title here! example of a Jinja template variable")


@app.errorhandler(404)
def page_not_found(e):
    logger.error(e)
    return render_template("error.html"), HTTPStatus.NOT_FOUND


@app.errorhandler(Exception)
def render_error(e):
    logger.error(e)
    return render_template("error.html"), HTTPStatus.INTERNAL_SERVER_ERROR


@app.after_request
def after_request(response):
    stage = os.environ["UNIVERSE"]
    if not stage == "qa":
        return response
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    return response


def make_json_response(service_response):
    if service_response.is_not_ok():
        json_dict = dict(error=service_response.error)
    else:
        json_dict = service_response.payload

    return app.response_class(
        response=json.dumps(json_dict),
        status=service_response.status,
        mimetype="application/json"
    )


# --- Local Routes ---
if is_local():
    # for flask to reload from disk in local mode
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
