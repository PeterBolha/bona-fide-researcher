from http import HTTPStatus
from typing import List

import requests

from models.author import Author
from models.institution import Institution
from models.name_matcher import NameMatcher
from models.search_results.orcid_search_result import OrcidSearchResult
from models.researcher import Researcher
from verification_modules.base_verification_module import BaseVerificationModule


class OrcidVerificationModule(BaseVerificationModule):
    def __init__(self, verbose: bool = False, requested_rows_count: int = 1000):
        super().__init__(verbose)
        self.module_name = "Orcid Verification Module"
        self._ORCID_API_URL = "https://pub.orcid.org/v3.0/expanded-search/"
        # critical threshold for which name is considered a match (X out of 100)
        self._NAME_MATCH_THRESHOLD = 65
        self._REQUESTED_ROWS_PAGE_LIMIT = 1000

        if requested_rows_count <= self._REQUESTED_ROWS_PAGE_LIMIT:
            self._REQUESTED_ROWS_COUNT = requested_rows_count
        else:
            self._REQUESTED_ROWS_COUNT = self._REQUESTED_ROWS_PAGE_LIMIT

    def print_reduced_result(self, result_items: List[Author]) -> None:
        for item in result_items:
            print(f"Matched researcher: {item}")
            print("----------------------------------------")

    def filter_results(self, unfiltered_items, researcher: Researcher) -> List[
        OrcidSearchResult]:
        filtered_items = []
        target_given_name, target_surname = (researcher.given_name,
                                             researcher.surname)

        # TODO - refactor for new author entity with Institution attr
        for item in unfiltered_items:
            affiliation = item.get("institution-name")
            affiliations = [Institution(affiliation)] if affiliation else []
            author_object = Author(item.get("given-names"),
                                   item.get("family-names"),
                                   affiliations,
                                   item.get("orcid-id"),
                                   item.get("email"))
            matched_result = OrcidSearchResult(author_object, item)
            name_matcher = NameMatcher(researcher.has_uncertain_name_order)

            candidate_given_name = item.get("given-names", "")
            candidate_surname = item.get("family-names", "")
            name_match_ratio = name_matcher.get_name_match_ratio(
                candidate_given_name, candidate_surname, target_given_name,
                target_surname)

            if name_match_ratio >= self._NAME_MATCH_THRESHOLD * 2:
                author_object.name_match_ratio = name_match_ratio
                filtered_items.append(matched_result)

        return filtered_items

    def get_researcher_info(self, researcher: Researcher) -> List[
        OrcidSearchResult]:
        result_items = []
        name_variations = [(researcher.given_name, researcher.surname)]

        if researcher.has_uncertain_name_order:
            name_variations.append((researcher.surname, researcher.given_name))

        for given_name, surname in name_variations:
            params = {
                "q": f"family-name:{surname} OR "
                     f"given-names:{given_name} OR "
                     f"orcid:{researcher.orcid} OR "
                     f"email:{researcher.email} OR "
                     f"current-institution-affiliation-name:"
                     f"{researcher.affiliation} OR "
                     f"past-institution-affiliation-name:"
                     f"{researcher.affiliation}",
                "start": 0,
                "rows": self._REQUESTED_ROWS_COUNT
            }
            headers = {"Accept": "application/json"}
            response = requests.get(self._ORCID_API_URL, params=params,
                                    headers=headers)
            response_data = response.json()

            if response.status_code != HTTPStatus.OK:
                print(
                    f"Verification of researcher {given_name} {surname} ("
                    f"given name - surname) failed with the response "
                    f"{response.status_code} - {response.text}")
            else:
                current_items = response_data['expanded-result']
                result_items.extend(current_items)

        filtered_result_items = self.filter_results(result_items, researcher)
        print("Obtained researcher info from ORCID")

        return filtered_result_items

    def verify(self, researcher: Researcher) -> List[OrcidSearchResult]:
        print("Extracting researcher information from ORCID")

        if not researcher.given_name:
            print(
                f"Missing researcher first name, skipping '{self.module_name}'")
            return []

        if not researcher.surname:
            print(
                f"Missing researcher last name, skipping '{self.module_name}'")
            return []

        return self.get_researcher_info(researcher)
