from abc import ABC
from http import HTTPStatus
from typing import List

import requests

from models.author import Author
from models.researcher import Researcher
from models.search_result import SearchResult
from verification_modules.base_verification_module import BaseVerificationModule


class CrossrefVerificationModule(BaseVerificationModule):
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.module_name = "Crossref Verification Module"
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

    def filter_results(self, unfiltered_items, researcher: Researcher) -> List[SearchResult]:
        filtered_items = []
        given_name, surname = researcher.given_name, researcher.surname

        for item in unfiltered_items:
            authors = item.get("author", [])
            matched_author = None
            author_objects = []

            for author in authors:
                author_object = Author(author.get("given"), author.get("family"), author.get("affiliation"))
                author_objects.append(author_object)

                default_value = str(object())  # Comparison with any string is possible and always returns False
                # Certain name order filtering
                has_regular_name_match = author.get("given", default_value) in given_name and author.get("family", default_value) in surname
                # Uncertain name order filtering (flip given name and surname)
                has_flipped_name_match = author.get("given", default_value) in surname and author.get("family", default_value) in given_name
                if has_regular_name_match or (researcher.has_uncertain_name_order and has_flipped_name_match):
                    matched_author = author_object



            if matched_author:
                search_result = SearchResult(matched_author,
                                             author_objects,
                                             item.get("DOI"),
                                             item.get("URL"),
                                             item.get("title"),
                                             item.get("institution"),
                                             item.get("publisher"),
                                             item)
                filtered_items.append(search_result)


        return filtered_items

    def get_researcher_info(self, researcher: Researcher) -> List[SearchResult]:

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
            response = requests.get('https://api.crossref.org/works', params=params)
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


    def verify(self, researcher: Researcher) -> List[SearchResult]:
        print("Extracting researcher information from Crossref")

        if not researcher.given_name:
            print(f"Missing researcher first name, skipping '{self.module_name}'")
            return []

        if not researcher.surname:
            print(f"Missing researcher last name, skipping '{self.module_name}'")
            return []

        return self.get_researcher_info(researcher)
