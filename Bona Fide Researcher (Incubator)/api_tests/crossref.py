from http import HTTPStatus

import requests

from api_tests.researcher import Researcher

FIRST_NAME = "Mihály"
LAST_NAME = "Héder"
EMAIL = "heder.mihaly@gtk.bme.hu"

RESEARCHER_MIHALY = Researcher(FIRST_NAME, LAST_NAME, EMAIL)

def get_general_info():
    # query by first name + last name
    params = {
        "query.author": f"{RESEARCHER_MIHALY.given_name} {RESEARCHER_MIHALY.surname}"
    }
    response = requests.get('https://api.crossref.org/works', params=params)

    if response.status_code != HTTPStatus.OK:
        print(response.status_code, response.text)
    else:
        print("Obtained general info:")
        print(response.json())

get_general_info()