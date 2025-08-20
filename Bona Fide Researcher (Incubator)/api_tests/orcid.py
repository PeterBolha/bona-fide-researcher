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
        "q": f"family-name:{RESEARCHER_MIHALY.surname} OR "
             f"given-names:{RESEARCHER_MIHALY.given_name} OR "
             f"orcid:{RESEARCHER_MIHALY.orcid} OR "
             f"email:{RESEARCHER_MIHALY.email} OR "
             f"current-institution-affiliation-name:{RESEARCHER_MIHALY} OR "
             f"past-institution-affiliation-name:{AFFILIATION}",
        "start": 0,
        "rows": 1000
    }
    headers = {"Accept": "application/json"}

    response = requests.get('https://pub.orcid.org/v3.0/expanded-search/', params=params, headers=headers)

    if response.status_code != HTTPStatus.OK:
        print(response.status_code, response.text)
    else:
        print("Obtained general info:")
        response_json = response.json()
        print(response.json())

get_general_info()