from typing import List, Tuple

from arxiv import Client, Result, Search, SortCriterion, SortOrder
from unidecode import unidecode

from models.author import Author
from models.name_matcher import NameMatcher
from models.researcher import Researcher
from models.search_results.arxiv_search_result import ArxivSearchResult
from models.search_results.unified_search_result import UnifiedSearchResult
from verification_modules.base_verification_module import BaseVerificationModule


class ArxivVerificationModule(BaseVerificationModule):
    def __init__(self, verbose: bool = False):
        super().__init__(verbose, "arXiv")
        self.module_name = "Arxiv Verification Module"
        # critical threshold for which name is considered a match (X out of 100)
        self._NAME_MATCH_THRESHOLD = 65
        self._MAX_RESULTS_LIMIT = 50

    def print_reduced_result(self, result_items: List[Author]) -> None:
        for item in result_items:
            print(f"Matched researcher: {item}")
            print("----------------------------------------")

    def _parse_name(self, full_name: str) -> Tuple[str, str]:
        name_parts = full_name.strip().split()

        if not len(name_parts) >= 2:
            return "", ""

        return name_parts[0], name_parts[-1]

    def search_arxiv_publications(self, author_name: str, max_results: int = 50,
                                  transliterate_name: bool = True) -> List[
        Result]:
        """
        Search for publications on ArXiv using the same parameters as the web
        interface.

        Args:
            author_name (str): The name of the author to search for
            max_results (int): Maximum number of results to return
            transliterate_name (bool): If True, transliterate names to
            replace special characters

        Returns:
            List of publications matching the search criteria
        """
        if transliterate_name:
            author_name = unidecode(author_name)

        search_query = f"au:\"{author_name}\""

        search = Search(
            query=search_query,
            max_results=max_results,
            sort_by=SortCriterion.SubmittedDate,
            sort_order=SortOrder.Descending
        )

        client = Client()
        results = list(client.results(search))
        return results

    def filter_results(self, unfiltered_items: List[Result],
                       researcher: Researcher) -> List[
        ArxivSearchResult]:
        filtered_items = []
        target_given_name, target_surname = (researcher.given_name,
                                             researcher.surname)

        # TODO - refactor for new author entity with Institution attr
        for item in unfiltered_items:
            name_matcher = NameMatcher(researcher.has_uncertain_name_order)
            author_objects = []
            matched_author = None

            for author in item.authors:
                candidate_given_name, candidate_surname = self._parse_name(
                    author.name)
                author_object = Author(candidate_given_name, candidate_surname)
                author_objects.append(author_object)

                name_match_ratio = name_matcher.get_name_match_ratio(
                    candidate_given_name, candidate_surname, target_given_name,
                    target_surname)

                if name_match_ratio >= self._NAME_MATCH_THRESHOLD * 2:
                    matched_author = author_object
                    matched_author.name_match_ratio = name_match_ratio

            if matched_author:
                matched_result = ArxivSearchResult(
                    matched_author=matched_author,
                    authors=author_objects,
                    doi=item.doi,
                    url=item.pdf_url,
                    arxiv_id=item.entry_id,
                    title=item.title,
                    summary=item.summary,
                    domains=item.categories,
                    raw_data=item)

                filtered_items.append(matched_result)

        return filtered_items

    def get_researcher_info(self, researcher: Researcher) -> List[
        ArxivSearchResult]:
        result_items = []
        name_variations = [(researcher.given_name, researcher.surname)]

        if researcher.has_uncertain_name_order:
            name_variations.append((researcher.surname, researcher.given_name))

        for given_name, surname in name_variations:
            full_name = f"{given_name} {surname}"
            current_items = self.search_arxiv_publications(full_name,
                                                      self._MAX_RESULTS_LIMIT,
                                                      True)
            result_items.extend(current_items)

        filtered_result_items = self.filter_results(result_items, researcher)
        print(f"Obtained researcher info from {self.data_source_name}")

        return filtered_result_items

    def get_unified_search_results(self, search_results: List[
        ArxivSearchResult]) -> List[UnifiedSearchResult]:
        unified_search_results = []

        for arxiv_search_result in search_results:
            unified_search_result = UnifiedSearchResult(
                matched_author=arxiv_search_result.matched_author,
                authors=set(arxiv_search_result.authors),
                doi=arxiv_search_result.doi,
                urls={arxiv_search_result.url, arxiv_search_result.arxiv_id},
                title=arxiv_search_result.title,
                descriptions={arxiv_search_result.summary},
                domains=set(arxiv_search_result.domains),
                raw_data=arxiv_search_result.raw_data,
                data_source=self.data_source_name
            )
            unified_search_results.append(unified_search_result)

        return unified_search_results

    def verify(self, researcher: Researcher) -> List[UnifiedSearchResult]:
        print(f"Extracting researcher information from {self.data_source_name}")

        if not researcher.given_name:
            print(
                f"Missing researcher first name, skipping '{self.module_name}'")
            return []

        if not researcher.surname:
            print(
                f"Missing researcher last name, skipping '{self.module_name}'")
            return []

        arxiv_researcher_info = self.get_researcher_info(researcher)
        return self.get_unified_search_results(arxiv_researcher_info)
