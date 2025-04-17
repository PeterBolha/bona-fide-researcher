from typing import Set

from abstracts.rankable import Rankable
from interfaces.imergeable import IMergeable
from models.institution import Institution
from models.researcher import Researcher


class Author(IMergeable["Author"], Rankable):
    def __init__(self, given_name: str, surname: str,
                 affiliations: Set[Institution], emails: Set[str] = None,
                 orcid: str = "") -> None:
        super().__init__()
        self.given_name = given_name
        self.given_name_alternatives = set()

        self.surname = surname
        self.surname_alternatives = set()

        if not affiliations:
            affiliations = set()
        self.affiliations = affiliations

        if not emails:
            emails = set()
        self.emails = emails
        self._email_rank_value = 1

        self.orcid = orcid
        self._orcid_rank_value = 1

        self.orcid_alternatives = set()

        self.name_match_ratio = 0

    def merge_with(self, other: "Author", debug_flag: bool = False) -> None:
        print("Merging author name")
        if not self.given_name and other.given_name:
            self.given_name = other.given_name
        elif self.given_name and other.given_name and self.given_name != other.given_name:
            self.given_name_alternatives.add(other.given_name)

        print("Merging author surname")
        if not self.surname and other.surname:
            self.surname = other.surname
        elif self.surname and other.surname and self.surname != other.surname:
            self.surname_alternatives.add(other.surname)

        # TODO - refine this merging, remove/join duplicate institutions
        print("Merging author affiliations (institutions)")
        self.affiliations.update(other.affiliations)

        print("Merging author emails")
        self.emails.update(other.emails)

        print("Merging author orcid")
        if not self.orcid and other.orcid:
            self.orcid = other.orcid
        # should not happen ever
        elif self.orcid and other.orcid and self.orcid != other.orcid:
            self.orcid_alternatives.add(other.orcid)
        print("Merging author - done")

    def __eq__(self, other):
        if self.orcid and other.orcid:
            return self.orcid == other.orcid
        else:
            return (self.given_name == other.given_name and self.surname ==
                    other.surname)

    def __hash__(self) -> int:
        return hash((self.given_name, self.surname))

    def __str__(self) -> str:
        affiliations_str = "Affiliations: \n" + "\n".join(f"\t - {str(institution)}" for institution in
                                     self.affiliations) if self.affiliations \
            else "?"
        return (
            f"Author: {self.given_name or "?"} (given name), "
            f"{self.surname or "?"} (surname)\n"
            f"{affiliations_str}\n"
            f"{self.orcid or "?"} (ORCID), "
            f"{self.emails or "?"} (email) [NAME MATCH - "
            f"{int(self.name_match_ratio)}/200]")

    # TODO - reevaluate rank calculation & rank values
    def calculate_internal_rank(self, researcher: Researcher) -> float:
        self.internal_rank = 0

        for affiliation in self.affiliations:
            self.internal_rank += affiliation.calculate_internal_rank(researcher)

        for _ in self.emails:
            self.internal_rank += self._email_rank_value

        if self.orcid:
            self.internal_rank += self._orcid_rank_value

        self.internal_rank += self.name_match_ratio

        return self.internal_rank
