from http import HTTPStatus
from typing import List

import requests

from models.author import Author
from models.name_matcher import NameMatcher
from models.researcher import Researcher
from models.crossref_search_result import CrossrefSearchResult
from verification_modules.base_verification_module import BaseVerificationModule


class CrossrefVerificationModule(BaseVerificationModule):
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.module_name = "Crossref Verification Module"
        self._CROSSREF_API_URL = "https://api.crossref.org/works"
        # critical threshold for which name is considered a match (X out of 100)
        self._NAME_MATCH_THRESHOLD = 65
        self.requested_rows_count = 1000

    def print_reduced_result(self, result_items):
        for item in result_items:
            print(f"Matched author: {item.get("matched_author")}")
            print(f"Authors: {item.get("author")}")
            print(f"DOI: {item.get("DOI", "?")}")
            print(f"URL: {item.get("URL", "?")}")
            print(f"Title: {item.get("title", "?")}")
            print(f"Institution: {item.get("institution", "?")}")
            print(f"Publisher: {item.get("publisher", "?")}")
            print("----------------------------------------")

    def filter_results(self, unfiltered_items, researcher: Researcher) -> List[CrossrefSearchResult]:
        filtered_items = []
        target_given_name, target_surname = researcher.given_name, researcher.surname
        # TODO - better format, maybe add as an input parameter
        name_match_threshold = 150

        for item in unfiltered_items:
            authors = item.get("author", [])
            matched_author = None
            author_objects = []

            for author in authors:
                author_object = Author(author.get("given"), author.get("family"), author.get("affiliation"))
                author_objects.append(author_object)
                name_matcher = NameMatcher(researcher.has_uncertain_name_order)

                candidate_given_name = author.get("given", "")
                candidate_surname = author.get("family", "")
                name_match_ratio = name_matcher.get_name_match_ratio(candidate_given_name, candidate_surname, target_given_name, target_surname)
                if name_match_ratio >= name_match_threshold:
                    author_object.name_match_ratio = name_match_ratio
                    matched_author = author_object



            if matched_author:
                search_result = CrossrefSearchResult(matched_author,
                                                     author_objects,
                                                     item.get("DOI"),
                                                     item.get("URL"),
                                                     item.get("title"),
                                                     item.get("institution"),
                                                     item.get("publisher"),
                                                     item)
                filtered_items.append(search_result)


        return filtered_items

    def get_researcher_info(self, researcher: Researcher) -> List[CrossrefSearchResult]:

        result_items = []
        cursor = "*"
        has_all_items = False
        given_name, surname = researcher.given_name, researcher.surname

        while not has_all_items:
            params = {
                "query.author": f"{given_name} {surname}",
                "cursor": cursor,
                "rows": self.requested_rows_count,
            }
            response = requests.get(self._CROSSREF_API_URL, params=params)
            response_data = response.json()

            if response.status_code != HTTPStatus.OK:
                print(f"Verification of researcher {given_name} {surname} failed with the response {response.status_code} - {response.text}")
                has_all_items = True
            else:
                current_items = response_data['message']['items']
                result_items.extend(current_items)
                cursor = response_data['message']['next-cursor']
                has_all_items = len(current_items) < self.requested_rows_count

        filtered_result_items = self.filter_results(result_items, researcher)
        print("Obtained researcher info from Crossref")

        return filtered_result_items


    def verify(self, researcher: Researcher) -> List[CrossrefSearchResult]:
        print("Extracting researcher information from Crossref")

        if not researcher.given_name:
            print(f"Missing researcher first name, skipping '{self.module_name}'")
            return []

        if not researcher.surname:
            print(f"Missing researcher last name, skipping '{self.module_name}'")
            return []

        return self.get_researcher_info(researcher)
