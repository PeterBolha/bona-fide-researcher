from typing import List


class Author:
    def __init__(self, given_name: str, surname: str, affiliation: List[str]) -> None:
        self.given_name = given_name
        self.surname = surname
        self.affiliation = affiliation
        self.name_match_ratio = 0

    def __str__(self) -> str:
        return f"Author: {self.given_name or "?"}, {self.surname or "?"}, {self.affiliation or "?"} (given name, surname, affiliation) [NAME MATCH - {int(self.name_match_ratio)}/200]"