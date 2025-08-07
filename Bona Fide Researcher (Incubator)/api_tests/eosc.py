from http import HTTPStatus

import requests

from models.researcher import Researcher

FIRST_NAME = "Mihály"
LAST_NAME = "Héder"
EMAIL = "heder.mihaly@gtk.bme.hu"
ORCID = "0000-0002-9979-9101"
AFFILIATION = "SZTAKI"

RESEARCHER_MIHALY = Researcher(FIRST_NAME, LAST_NAME, EMAIL)

# EOSC has no official documented API, requests from the website frontend are routed through an API on the background
# Reverse-engineering this request yielded this result
def get_general_info():
    # query by first name + last name
    params = {
        "query": f"{RESEARCHER_MIHALY.given_name} {RESEARCHER_MIHALY.surname}",
        "exact": "false",
        "catalogue": "all",
        "page": 0,
        "orderBy": "relevance",
        "order": "desc",
    }
    response = requests.get('https://api.open-science-cloud.ec.europa.eu/action/catalogue/items', params=params)

    if response.status_code != HTTPStatus.OK:
        print(response.status_code, response.text)
    else:
        print("Obtained general info:")
        response_json = response.json()
        print(response.json())

get_general_info()