from typing import List


class Author:
    def __init__(self, given_name: str, surname: str, affiliation: List[str]) -> None:
        self.given_name = given_name
        self.surname = surname
        self.affiliation = affiliation

    def __str__(self) -> str:
        return f"Author: {self.given_name or "?"}, {self.surname or "?"}, {self.affiliation or "?"} (given name, surname, affiliation)"