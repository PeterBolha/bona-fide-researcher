import json
import math
from argparse import Namespace
from http import HTTPStatus

from flask import Flask, Request, Response, jsonify, request

from enums.result_presentation_mode import ResultPresentationMode
from verify_eduperson import verify_eduperson

app = Flask(__name__)


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

@app.route("/verify-eduperson", methods=["GET"])
def verify_eduperson_endpoint():
    uncertain_name_order = parse_boolean_variable(request, "uncertain_name_order")
    if isinstance(uncertain_name_order, Response):
        return uncertain_name_order

    verbose = parse_boolean_variable(request, "verbose")
    if isinstance(verbose, Response):
        return verbose

    verify_email_domain = parse_boolean_variable(request, "verify_email_domain")
    if isinstance(verify_email_domain, Response):
        return verify_email_domain

    limit_results = parse_integer_variable(request, "limit_results")
    if isinstance(limit_results, Response):
        return limit_results

    args = Namespace(
        given_name=request.form.get("given_name"),
        surname=request.form.get("surname"),
        email=request.form.get("email"),
        orcid=request.form.get("orcid"),
        affiliation=request.form.get("affiliation"),
        uncertain_name_order=uncertain_name_order,
        verbose=verbose,
        verify_email_domain=verify_email_domain,
        limit_results=limit_results,
    )

    results = verify_eduperson(args, ResultPresentationMode.API)
    return jsonify(results)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
