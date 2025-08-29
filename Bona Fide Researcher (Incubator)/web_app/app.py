"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
import threading
import uuid
from argparse import Namespace
from http import HTTPStatus
from typing import Tuple

import requests
from flask import Flask, Request, Response, g, jsonify

from enums.job_status import JobStatus
from enums.result_presentation_mode import ResultPresentationMode
from researcher_relationship_graph import get_researcher_relationship_graph_data
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
                               f"integer greater than 0. Problematic request "
                               f"part: {request_params}",
                               status=HTTPStatus.BAD_REQUEST)

    if not request_params.get("callback_url"):
        return False, Response(
            f"Missing 'callback_url' parameter. The search result is returned "
            f"to the callback URL so it must be provided. Problematic request "
            f"part: {request_params}",
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


def start_background_jobs(func, namespace_args_list: list[Namespace]) -> (
        tuple)[Response, HTTPStatus]:
    jobs = app.jobs
    job_responses = []

    for namespace_args in namespace_args_list:
        callback_url = namespace_args.callback_url
        job_id = start_background_job(jobs,
                                      func,
                                      args=(namespace_args,
                                            ResultPresentationMode.API),
                                      callback_url=callback_url)
        job_responses.append({"job_id": job_id,
                              "researcher_name": namespace_args.full_name,
                              "status": JobStatus.RUNNING.name,
                              "message": (f"Your job has been submitted and "
                                          f"assigned an ID: {job_id}. Please "
                                          f"wait for the response "
                                          f"on the callback URL: "
                                          f"{callback_url}. You can track the "
                                          f"progress of the job by calling "
                                          f"the status endpoint:  "
                                          f"/status/<job_id>")})

    return jsonify(job_responses), HTTPStatus.ACCEPTED


def get_normalized_researcher_request():
    # g is filled with jwt data by the check_jwt_auth decorator if auth is
    # successful
    request_params = g.jwt_payload

    researcher_requests = request_params.get("researchers")
    # presume there is just a single researcher instead of a list
    if not researcher_requests:
        researcher_requests = [request_params]

    return researcher_requests

@app.route("/verify-eduperson", methods=["GET"])
@check_jwt_auth
def verify_eduperson_endpoint():
    namespace_args_list = []
    researcher_requests = get_normalized_researcher_request()

    for researcher_request in researcher_requests:
        valid_params, response = has_valid_params(researcher_request)
        if not valid_params:
            return response

        full_name = (researcher_request.get("given_name", "") + " " +
                     researcher_request.get("surname", ""))
        namespace_args = Namespace(
            given_name=researcher_request.get("given_name"),
            surname=researcher_request.get("surname"),
            full_name=full_name,
            email=researcher_request.get("email"),
            orcid=researcher_request.get("orcid"),
            affiliation=researcher_request.get("affiliation"),
            uncertain_name_order=researcher_request.get("uncertain_name_order",
                                                    False),
            verbose=researcher_request.get("verbose", False),
            verify_email_domain=researcher_request.get("verify_email_domain",
                                                   False),
            limit_results=researcher_request.get("limit_results", 10),
            callback_url = researcher_request.get("callback_url")
        )

        namespace_args_list.append(namespace_args)

    return start_background_jobs(verify_eduperson, namespace_args_list)


@app.route("/status/<job_id>")
def get_job_status(job_id: str):
    job_status_data = app.jobs.get(job_id,
                                   {"status": JobStatus.NOT_FOUND.name})
    return jsonify(job_status_data)

@app.route("/researcher-relationship-graph")
@check_jwt_auth
def get_researcher_relationship_graph():
    namespace_args_list = []
    researcher_requests = get_normalized_researcher_request()

    for researcher_request in researcher_requests:
        valid_params, response = has_valid_params(researcher_request)
        if not valid_params:
            return response

        full_name = researcher_request.get("full_name")
        namespace_args = Namespace(
            full_name=full_name,
            max_relationship_depth=researcher_request.get(
                "max_relationship_depth", 3),
            callback_url=researcher_request.get("callback_url")
        )

        namespace_args_list.append(namespace_args)

    return start_background_jobs(get_researcher_relationship_graph_data,
                                 namespace_args_list)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
