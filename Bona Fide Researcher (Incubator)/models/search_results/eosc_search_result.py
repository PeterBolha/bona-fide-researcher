"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
from typing import Any, List, Set

from models.author import Author
from models.researcher import Researcher
from models.search_results.search_result import SearchResult


class EoscSearchResult(SearchResult):
    def __init__(self, matched_author: Author, authors: List[Author], doi: str,
                 urls: Set[str], publishers: Set[str], title: str, domains: List[str],
                 raw_data: Any):
        super().__init__()
        self.matched_author = matched_author
        self.authors = authors
        self.doi = doi
        self.urls = urls
        self.publishers = publishers
        self.title = title
        self.domains = domains

        self.raw_data = raw_data

    def calculate_internal_rank(self, researcher_candidate: Researcher):
        self.internal_rank = 0

        # TODO - reevaluate these metrics
        author_name_match_ratio = self.matched_author.name_match_ratio
        attribute_rank_value = 0.05 * author_name_match_ratio
        self.internal_rank += author_name_match_ratio

        # award a point for the presence of these attributes
        attributes = ['doi', 'urls', 'title', 'publishers']

        for attr in attributes:
            if getattr(self, attr):
                self.internal_rank += attribute_rank_value


    def print(self, verbose: bool = False):
        print("----------------------------------------")

        if verbose:
            print(self.raw_data)

        else:
            print("Matched author:")
            print(self.matched_author)
            print(f"DOI: {self.doi or "?"}")
            print(f"URLS: {self.urls or "?"}")
            print(f"Title: {self.title or "?"}")
            print(f"Domains: {self.domains or "?"}")
            print(f"Publishers: {self.publishers or "?"}")

        print("----------------------------------------")
