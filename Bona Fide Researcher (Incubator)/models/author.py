from typing import List

from models.institution import Institution


# Crossref & ORCID API Entity & EOSC
class Author:
    def __init__(self, given_name: str, surname: str, affiliations: List[Institution], email: str = "", orcid: str = "") -> None:
        self.given_name = given_name
        self.surname = surname
        self.affiliations = affiliations
        self.email = email
        self.orcid = orcid
        self.name_match_ratio = 0

    def __str__(self) -> str:
        affiliations_str = ", ".join(str(institution) for institution in self.affiliations) if self.affiliations else "?"
        return f"Author: {self.given_name or "?"}, {self.surname or "?"}, {affiliations_str}, {self.orcid}, {self.email or "?"} (given name, surname, affiliation, orcid, email) [NAME MATCH - {int(self.name_match_ratio)}/200]"