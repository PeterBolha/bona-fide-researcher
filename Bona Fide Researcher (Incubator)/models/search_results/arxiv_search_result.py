from typing import Any, List

from models.author import Author
from models.researcher import Researcher
from models.search_results.search_result import SearchResult


class ArxivSearchResult(SearchResult):
    def __init__(self, matched_author: Author, authors: List[Author], doi: str,
                 url: str, arxiv_id: str, title: str, summary: str, domains: List[str],
                 raw_data: Any):
        super().__init__()
        self.matched_author = matched_author
        self.authors = authors
        self.doi = doi
        self.url = url
        self.arxiv_id = arxiv_id
        self.title = title
        self.summary = summary
        self.domains = domains

        self.raw_data = raw_data

    def calculate_internal_rank(self, researcher_candidate: Researcher):
        self.internal_rank = 0

        # TODO - reevaluate these metrics
        author_name_match_ratio = self.matched_author.name_match_ratio
        attribute_rank_value = 0.05 * author_name_match_ratio
        self.internal_rank += author_name_match_ratio

        # award a point for the presence of these attributes
        attributes = ['doi', 'url', 'arxiv_id', 'title', 'summary', 'domains']

        for attr in attributes:
            if getattr(self, attr):
                self.internal_rank += attribute_rank_value

        if self.matched_author.affiliations:
            # TODO make affiliation match affect ranking
            # researcher_candidate.affiliation = self.matched_author.affiliation
            self.internal_rank += attribute_rank_value

    def print(self, verbose: bool = False):
        print("----------------------------------------")

        if verbose:
            print(self.raw_data)

        else:
            print("Matched author:")
            print(self.matched_author)
            print(f"DOI: {self.doi or "?"}")
            print(f"URL: {self.url or "?"}")
            print(f"arXiv ID: {self.arxiv_id or "?"}")
            print(f"Title: {self.title or "?"}")
            print(f"Summary: {self.summary or "?"}")
            print(f"Domains: {self.domains or "?"}")

        print("----------------------------------------")
