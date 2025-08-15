import json
import math
from argparse import Namespace
from http import HTTPStatus
from typing import Tuple

from flask import Flask, Request, Response, g, jsonify, request

from enums.result_presentation_mode import ResultPresentationMode
from utils.config_loader import load_config
from verify_eduperson import verify_eduperson
from web_app.jwt_auth import check_jwt_auth

APP_CFG_FILEPATH = "./configs/config.yaml"

app_config = load_config(APP_CFG_FILEPATH)
app = Flask(__name__)
app.config.update(app_config)


@app.route("/")
def home():
    return "Hello World test flask app!"

def parse_boolean_variable(request: Request, variable_name: str) -> (bool |
                                                                     Response):
    variable_value = request.form.get(variable_name, "False")
    if variable_value in ["true", "True"]:
        return True
    elif variable_value in ["false", "False"] or variable_value is None:
        return False
    else:
        return Response(f"Invalid '{variable_name}' value: "
                        f"{variable_value}. The value should be a "
                        f"boolean (true/True/false/False).",
                        status=HTTPStatus.BAD_REQUEST)

def parse_integer_variable(request: Request, variable_name: str) -> (int |
                                                                     Response):
    variable_value = request.form.get(variable_name, None)
    if not variable_value:
        return -1

    try:
        int_value = int(variable_value)
        if int_value < 1:
            raise ValueError

        return int_value
    except (ValueError, TypeError):
        return Response(f"Invalid '{variable_name}' value: "
                        f"{variable_value}. The value should be an integer "
                        f"greater than 0.",
                        status=HTTPStatus.BAD_REQUEST)

def has_valid_params(request_params: dict) -> Tuple[bool, Response]:
    limit_results = request_params.get("limit_results")

    if limit_results is not None and limit_results < 1:
        return False, Response(f"Invalid 'limit_results' value: "
                        f"{limit_results}. The value should be an integer "
                        f"greater than 0.",
                        status=HTTPStatus.BAD_REQUEST)

    placeholder_response = Response()
    return  True, placeholder_response

@app.route("/verify-eduperson", methods=["GET"])
@check_jwt_auth
def verify_eduperson_endpoint():
    # g is filled with jwt data by the check_jwt_auth decorator if auth is
    # successful
    request_params = g.jwt_payload

    valid_params, response = has_valid_params(request_params)
    if not valid_params:
        return response

    args = Namespace(
        given_name=request_params.get("given_name"),
        surname=request_params.get("surname"),
        email=request_params.get("email"),
        orcid=request_params.get("orcid"),
        affiliation=request_params.get("affiliation"),
        uncertain_name_order=request_params.get("uncertain_name_order"),
        verbose=request_params.get("verbose"),
        verify_email_domain=request_params.get("verify_email_domain"),
        limit_results=request_params.get("limit_results"),
    )

    results = verify_eduperson(args, ResultPresentationMode.API)
    return jsonify(results)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
