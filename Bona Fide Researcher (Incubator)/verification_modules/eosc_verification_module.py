from http import HTTPStatus
from typing import List

import requests

from models.author import Author
from models.search_results.eosc_search_result import EoscSearchResult
from models.institution import Institution
from models.name_matcher import NameMatcher
from models.researcher import Researcher
from verification_modules.base_verification_module import BaseVerificationModule


class EoscVerificationModule(BaseVerificationModule):
    def __init__(self, verbose: bool = False, requested_rows_count: int = 20):
        super().__init__(verbose)
        self.module_name = "EOSC Resource Hub Verification Module"
        self._EOSC_API_URL = ("https://api.open-science-cloud.ec.europa.eu"
                              "/action/catalogue/items")
        # critical threshold for which name is considered a match (X out of 100)
        self._NAME_MATCH_THRESHOLD = 65
        # more than 20 is prohibited by the EOSC API
        self._REQUESTED_ROWS_PAGE_LIMIT = 20

        if requested_rows_count <= self._REQUESTED_ROWS_PAGE_LIMIT:
            self._REQUESTED_ROWS_COUNT = requested_rows_count
        else:
            self._REQUESTED_ROWS_COUNT = self._REQUESTED_ROWS_PAGE_LIMIT

    def print_reduced_result(self, result_items: List[Author]) -> None:
        for item in result_items:
            print(f"Matched researcher: {item}")
            print("----------------------------------------")

    def filter_results(self, unfiltered_items, researcher: Researcher) -> List[
        EoscSearchResult]:
        filtered_items = []
        name_match_threshold = self._NAME_MATCH_THRESHOLD * 2
        target_given_name, target_surname = (researcher.given_name,
                                             researcher.surname)
        for item in unfiltered_items:
            authors = item.get("source", {}).get("contributions", [])
            matched_author = None
            author_objects = []

            for author in authors:
                if not author.get("is_listed_author", False):
                    continue

                person = author.get("person", {})
                person_names_split = person.get("full_name", "").split()

                if not len(person_names_split) >= 2:
                    continue

                candidate_given_name = person_names_split[0]
                candidate_surname = person_names_split[-1]
                name_matcher = NameMatcher(researcher.has_uncertain_name_order)

                name_match_ratio = name_matcher.get_name_match_ratio(
                    candidate_given_name, candidate_surname, target_given_name,
                    target_surname)
                data_source = item.get("source", {})

                institutions = []
                orgs = data_source.get("relevant_organizations", [])
                for org in orgs:
                    institution = Institution(org.get("name"), org.get("ror"),
                                              org.get("isni"))
                    institutions.append(institution)

                author_object = Author(candidate_given_name,
                                       candidate_surname,
                                       affiliations=institutions,
                                       orcid=person.get("orcid"))
                author_objects.append(author_object)

                if name_match_ratio >= name_match_threshold:
                    author_object.name_match_ratio = name_match_ratio
                    matched_author = author_object

                if matched_author:
                    raw_domains = data_source.get("domain", [])
                    domains = [d.get("domain", "?") for d in raw_domains]

                    doi = "?"
                    identifiers = data_source.get("identifiers", [])
                    for identifier in identifiers:
                        if identifier.get("scheme", "?") == "doi":
                            doi = identifier.get("value", "?")
                            break

                    title = "?"
                    titles_collection = data_source.get("titles", {})
                    for titles in titles_collection.values():
                        if len(titles) > 0:
                            title = titles[0]

                    urls = []
                    publishers = set([])
                    manifestations = data_source.get("manifestations", [])
                    for manifestation in manifestations:
                        url = manifestation.get("url")
                        if url:
                            urls.append(url)

                        publisher = manifestation.get("venue", {}).get("name")
                        if publisher:
                            publishers.add(publisher)

                    search_result = EoscSearchResult(matched_author,
                                                     author_objects,
                                                     doi,
                                                     urls,
                                                     publishers,
                                                     title,
                                                     domains,
                                                     item)

                    filtered_items.append(search_result)

        return filtered_items

    def get_researcher_info(self, researcher: Researcher) -> List[
        EoscSearchResult]:
        result_items = []
        given_name = researcher.given_name
        surname = researcher.surname

        start_page = 0
        has_all_items = False
        # TODO remove this limit
        page_limit = 5
        while not has_all_items and start_page < page_limit:
            print(f"start_page: {start_page + 1} of {page_limit}")
            params = {
                # order of names does not matter in EOSC search
                "query": f"{given_name} {surname}",
                "exact": "false",
                "catalogue": "all",
                "page": start_page,
                "orderBy": "relevance",
                "order": "desc",
            }
            response = requests.get(self._EOSC_API_URL, params=params)
            response_data = response.json()

            if response.status_code != HTTPStatus.OK:
                print(
                    f"Verification of researcher {given_name} {surname} "
                    f"failed with the response {response.status_code} - "
                    f"{response.text}")
                has_all_items = True
            else:
                current_items = response_data['result']['items']
                result_items.extend(current_items)
                start_page += 1
                has_all_items = len(current_items) < self._REQUESTED_ROWS_COUNT

        filtered_result_items = self.filter_results(result_items, researcher)
        print("Obtained researcher info from EOSC Resource Hub")

        return filtered_result_items

    def verify(self, researcher: Researcher) -> List[EoscSearchResult]:
        print("Extracting researcher information from EOSC Resource Hub")

        if not researcher.given_name:
            print(
                f"Missing researcher first name, skipping '{self.module_name}'")
            return []

        if not researcher.surname:
            print(
                f"Missing researcher last name, skipping '{self.module_name}'")
            return []

        return self.get_researcher_info(researcher)
