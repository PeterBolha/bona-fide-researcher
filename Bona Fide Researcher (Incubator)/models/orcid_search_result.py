from typing import Any

from models.author import Author
from models.researcher import Researcher
from models.search_result import SearchResult


class OrcidSearchResult(SearchResult):
    def __init__(self, matched_author: Author, raw_data: Any):
        super().__init__()
        self.matched_author = matched_author
        self.raw_data = raw_data

    def calculate_internal_rank(self, researcher_candidate: Researcher):
        self.internal_rank = 0

        # TODO - reevaluate these metrics
        author_name_match_ratio = self.matched_author.name_match_ratio
        attribute_rank_value = 0.05 * author_name_match_ratio
        self.internal_rank += author_name_match_ratio

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

        print("----------------------------------------")
