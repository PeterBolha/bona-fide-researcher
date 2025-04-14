from typing import Set

from interfaces.imergeable import IMergeable
from models.institution import Institution


class Author(IMergeable["Author"]):
    def __init__(self, given_name: str, surname: str,
                 affiliations: Set[Institution], emails: Set[str]=None,
                 orcid: str = "") -> None:
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
        self.orcid = orcid
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
        if debug_flag:
            print("debug")

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
        if self.orcid:
            return hash(self.orcid)
        else:
            return hash((self.given_name, self.surname))

    def __str__(self) -> str:
        affiliations_str = ", ".join(str(institution) for institution in
                                     self.affiliations) if self.affiliations \
            else "?"
        return (
            f"Author: {self.given_name or "?"} (given name), "
            f"{self.surname or "?"} (surname), "
            f"{affiliations_str} (affiliations), {self.orcid or "?"} (ORCID), "
            f"{self.email or "?"} (email) [NAME MATCH - "
            f"{int(self.name_match_ratio)}/200]")
