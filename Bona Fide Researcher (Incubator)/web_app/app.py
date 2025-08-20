import threading
import uuid
from argparse import Namespace
from http import HTTPStatus
from typing import Tuple

import requests
from flask import Flask, Request, Response, current_app, g, jsonify

from enums.job_status import JobStatus
from enums.result_presentation_mode import ResultPresentationMode
from utils.config_loader import load_config
from verify_eduperson import verify_eduperson
from web_app.jwt_auth import check_jwt_auth

APP_CFG_FILEPATH = "./configs/config.yaml"

app_config = load_config(APP_CFG_FILEPATH)
app = Flask(__name__)
app.config.update(app_config)
app.jobs = {}


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
                               f"{limit_results}. The value should be an "
                               f"integer "
                               f"greater than 0.",
                               status=HTTPStatus.BAD_REQUEST)

    if not request_params.get("callback_url"):
        return False, Response(
            f"Missing 'callback_url' parameter. The search result is returned "
            f"to the callback URL so it must be provided.",
            status=HTTPStatus.BAD_REQUEST)

    placeholder_response = Response()
    return True, placeholder_response


def long_job_executor(jobs, job_id, func, args=None, kwargs=None,
                      callback_url=None):
    args = args or ()
    kwargs = kwargs or {}
    try:
        result = func(*args, **kwargs)

        jobs[job_id] = {
            "status": JobStatus.FINISHED_SUCCESS.name,
            "result": result
        }

        try:
            requests.post(callback_url, json={
                "job_id": job_id,
                "status": JobStatus.FINISHED_SUCCESS.name,
                "result": result
            })
        except Exception as e:
            jobs[job_id]["callback_error"] = str(e)

    except Exception as e:
        jobs[job_id] = {
            "status": JobStatus.FINISHED_ERROR.name,
            "error_message": str(e)
        }


def start_background_job(jobs, func, args=None, kwargs=None, callback_url=None):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": JobStatus.RUNNING.name}

    thread = threading.Thread(
        target=long_job_executor,
        args=(jobs, job_id, func, args, kwargs, callback_url),
        daemon=True
    )
    thread.start()

    return job_id


@app.route("/verify-eduperson", methods=["GET"])
@check_jwt_auth
def verify_eduperson_endpoint():
    # g is filled with jwt data by the check_jwt_auth decorator if auth is
    # successful
    request_params = g.jwt_payload

    valid_params, response = has_valid_params(request_params)
    if not valid_params:
        return response

    namespace_args = Namespace(
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

    callback_url = request_params.get("callback_url")
    jobs = app.jobs
    job_id = start_background_job(jobs,
                                  verify_eduperson,
                                  args=(namespace_args,
                                        ResultPresentationMode.API),
                                  callback_url=callback_url)

    return (jsonify({"job_id": job_id, "status": JobStatus.RUNNING.name,
                     "message": f"Your job has been submitted and assigned an "
                                f"ID: {job_id}. Please wait for the response "
                                f"on the callback URL: {callback_url}. You "
                                f"can track the progress of the job by "
                                f"calling the status endpoint: "
                                f"/status/<job_id>"}),
            HTTPStatus.ACCEPTED)


@app.route("/status/<job_id>")
def get_job_status(job_id: str):
    job_status_data = app.jobs.get(job_id,
                                           {"status": JobStatus.NOT_FOUND.name})
    return jsonify(job_status_data)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
