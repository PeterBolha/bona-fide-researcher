from typing import List

# Crossref & ORCID API Entity
class Author:
    def __init__(self, given_name: str, surname: str, affiliation: List[str], email: str = "", orcid: str = "") -> None:
        self.given_name = given_name
        self.surname = surname
        self.affiliation = affiliation
        self.email = email
        self.orcid = orcid
        self.name_match_ratio = 0

    def __str__(self) -> str:
        return f"Author: {self.given_name or "?"}, {self.surname or "?"}, {self.affiliation or "?"}, {self.orcid}, {self.email or "?"} (given name, surname, affiliation, orcid, email) [NAME MATCH - {int(self.name_match_ratio)}/200]"