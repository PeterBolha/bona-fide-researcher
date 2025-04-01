from typing import List

from models.researcher import Researcher
from models.search_result import SearchResult


class SearchResultsAggregator:
    def __init__(self, researcher: Researcher, verbose: bool = False):
        self.researcher = researcher
        self.search_results = []
        self.verbose = verbose

    def add_results(self, search_results: List[SearchResult]):
        self.search_results += search_results

    def _rank_results(self):
        for result in self.search_results:
            result.calculate_internal_rank(self.researcher)

    def _sort_results(self):
        self.search_results = sorted(self.search_results, reverse=True)

    def _print_search_results(self):
        for result in self.search_results:
            result.print(self.verbose)

    def present_search_results(self):
        self._rank_results()
        self._sort_results()
        self._print_search_results()