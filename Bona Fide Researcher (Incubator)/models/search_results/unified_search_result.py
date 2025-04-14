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
        self.authors = authors
        self.doi = doi
        self.urls = urls

        self.title = title
        self.title_alternatives = set()

        self.publishers = publishers

        if not domains:
            domains = set()
        self.domains = domains

        self.data_source = data_source
        self.raw_data = raw_data

    # TODO - implement fully
    def merge_with(self, other: "UnifiedSearchResult", debug_flag: bool = False) -> None:
        print("Merging search result author")
        self.matched_author.merge_with(other.matched_author, debug_flag)
        print("Merged search result author")

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
        self.raw_data += f"{separator}SOURCE: ({self.data_source}) -> {self.raw_data}"

    # TODO implement ranking calculation
    def calculate_internal_rank(self, researcher: Researcher) -> None:
        pass

    def print(self, verbose: bool = False) -> None:
        print("########################################")

        if verbose:
            print(self.raw_data)

        else:
            print("Matched author:")
            print(self.matched_author)
            print(f"DOI: {self.doi or "?"}")

            if self.urls:
                print(f"URLS: ")
                for url in self.urls:
                    print(f"\t- {url}")
            else:
                print(f"URLS: ?")

            print(f"Title: {self.title or "?"}")

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

        print("########################################")
