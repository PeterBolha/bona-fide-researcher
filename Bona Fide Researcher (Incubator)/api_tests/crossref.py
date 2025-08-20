"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
from http import HTTPStatus

import requests

from models.researcher import Researcher

FIRST_NAME = "Mihály"
LAST_NAME = "Héder"
EMAIL = "heder.mihaly@gtk.bme.hu"
ORCID = "0000-0002-9979-9101"
AFFILIATION = "SZTAKI"

RESEARCHER_MIHALY = Researcher(FIRST_NAME, LAST_NAME, EMAIL)

def get_general_info():
    # query by first name + last name
    params = {
        "query.author": f"{RESEARCHER_MIHALY.given_name} {RESEARCHER_MIHALY.surname}",
        # "filter": f"orcid:{ORCID}"
        "query.affiliation": f"{AFFILIATION}"
    }
    response = requests.get('https://api.crossref.org/works', params=params)

    if response.status_code != HTTPStatus.OK:
        print(response.status_code, response.text)
    else:
        print("Obtained general info:")
        response_json = response.json()
        print(response.json())

get_general_info()