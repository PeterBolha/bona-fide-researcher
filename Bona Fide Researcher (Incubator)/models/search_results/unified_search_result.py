from typing import Any, Set

from interfaces.imergeable import IMergeable
from models.author import Author
from models.researcher import Researcher
from models.search_results.search_result import SearchResult


class UnifiedSearchResult(SearchResult, IMergeable["UnifiedSearchResult"]):
    def __init__(self, matched_author: Author = None,
                 authors: Set[Author] = None, doi: str = None,
                 urls: Set[str] = None, title: str = None,
                 publishers: Set[str] = None,
                 domains: Set[str] = None, raw_data: Any = None,
                 data_source: str = "?"):
        super().__init__()
        self.matched_author = matched_author
        self._matched_author_rank_weight = 1

        if not authors:
            authors = set()
        self.authors = authors
        self._coauthor_rank_weight = 0.2

        self.doi = doi
        self._doi_rank_value = 1

        if not urls:
            urls = set()
        self.urls = urls
        self._url_rank_value = 1

        self.title = title
        self._title_rank_value = 1

        self.title_alternatives = set()
        self._title_alt_rank_value = 1

        if not publishers:
            publishers = set()
        self.publishers = publishers
        self._publisher_rank_value = 1

        if not domains:
            domains = set()
        self.domains = domains
        self._domain_rank_value = 1

        self.data_source = data_source

        self.raw_data = raw_data
        self._raw_data_rank_value = 0

    # TODO - implement fully
    def merge_with(self, other: "UnifiedSearchResult",
                   debug_flag: bool = False) -> None:
        self.matched_author.merge_with(other.matched_author, debug_flag)

        # TODO - high complexity, unreliable matching - fix! 
        # for current_author in self.authors:
        #     for external_author in other.authors:
        #         current_author.merge_with(external_author)

        if not self.doi and other.doi:
            self.doi = other.doi

        self.urls.update(other.urls)

        if not self.title and other.title:
            self.title = other.title
        elif self.title and other.title and self.title != other.title:
            self.title_alternatives.update(other.title)

        self.publishers.update(other.publishers)
        self.domains.update(other.domains)

        separator = "\n--------------------\n"

        self.raw_data = str(self.raw_data)
        self.raw_data += (f"{separator}SOURCE: ({self.data_source}) -> "
                          f"{self.raw_data}")

    # TODO - reevaluate rank calculation & rank values
    # Quality of DAta source could be incorporated into ranking
    # raw data is always present, should be ranked?
    def calculate_internal_rank(self, researcher: Researcher) -> float:
        self.internal_rank = 0

        if self.matched_author:
            self.internal_rank += (self._matched_author_rank_weight *
                                   self.matched_author.calculate_internal_rank(
                researcher))

        for author in self.authors:
            self.internal_rank += author.calculate_internal_rank(researcher) * self._coauthor_rank_weight

        if self.doi:
            self.internal_rank += self._doi_rank_value

        for _ in self.urls:
            self.internal_rank += self._url_rank_value

        if self.title:
            self.internal_rank += self._title_rank_value

        for _ in self.title_alternatives:
            self.internal_rank += self._title_alt_rank_value

        for _ in self.publishers:
            self.internal_rank += self._publisher_rank_value

        for _ in self.domains:
            self.internal_rank += self._domain_rank_value

        return self.internal_rank

    def print(self, verbose: bool = False) -> None:
        print("########################################")

        if verbose:
            print(self.raw_data)

        else:
            # print("Matched author:")
            # print(self.matched_author)
            print(f"Title: {self.title or "?"}")
            print(f"DOI: {self.doi or "?"}")

            if self.urls:
                print(f"URLS: ")
                for url in self.urls:
                    print(f"\t- {url}")
            else:
                print(f"URLS: ?")


            if self.title_alternatives:
                print(f"Alternative titles: ")
                for alt_title in self.title_alternatives:
                    print(f"\t- {alt_title}")

            if self.publishers:
                print(f"Publishers: ")
                for publisher in self.publishers:
                    print(f"\t- {publisher}")
            else:
                print(f"Publishers: ?")

            if self.domains:
                print(f"Domains: ")
                for domain in self.domains:
                    print(f"\t- {domain}")
            else:
                print(f"Domains: ?")
