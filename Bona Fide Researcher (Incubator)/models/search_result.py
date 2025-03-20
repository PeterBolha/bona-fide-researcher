from typing import Any, List

from models.author import Author
from models.researcher import Researcher


class SearchResult:
    def __init__(self, matched_author: Author, authors: List[Author], doi: str, url: str, title: str, institution: str, publisher: str, raw_data: Any):
        self.matched_author = matched_author
        self.authors = authors
        self.doi = doi
        self.url = url
        self.title = title
        self.institution = institution
        self.publisher = publisher

        self.raw_data = raw_data

        self.internal_rank = 0

    def __lt__(self, other):  # Defines sorting order (ascending by internal rank)
        return self.internal_rank < other.internal_rank

    def __eq__(self, other):  # Needed for full sorting support
        return self.internal_rank == other.internal_rank

    # TODO - implement rank calculation
    def calculate_internal_rank(self, researcher_candidate: Researcher):
        self.internal_rank = 0

        # award a point for the presence of these attributes
        attributes = ['doi', 'url', 'title', 'institution', 'publisher']

        for attr in attributes:
            if getattr(self, attr):
                self.internal_rank += 1

        # TODO - name & surname match given order
        # TODO - name & surname match exactly without accents
        # TODO - name & surname match exactly with accents



    def print(self, verbose: bool = False):
        print("----------------------------------------")

        if verbose:
            print(self.raw_data)

        else:
            print("Matched author:")
            print(self.matched_author)
            print("All authors:")
            for author in self.authors:
                print(author)
            print(f"DOI: {self.doi or "?"}")
            print(f"URL: {self.url or "?"}")
            print(f"Title: {self.title or "?"}")
            print(f"Institution: {self.institution or "?"}")
            print(f"Publisher: {self.publisher or "?"}")

        print("----------------------------------------")
