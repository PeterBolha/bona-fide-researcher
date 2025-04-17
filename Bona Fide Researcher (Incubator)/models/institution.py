from abstracts.rankable import Rankable
from models.researcher import Researcher


class Institution(Rankable):
    def __init__(self, name: str, ror: str = None, isni: str = None) -> None:
        super().__init__()
        self.name = name
        self._name_rank_value = 1

        # Research Organization Registry ID
        self.ror = ror
        self._ror_rank_value = 1

        # International Standard Name Identifier
        self.isni = isni
        self._isni_rank_value = 1


    def __eq__(self, other: "Institution") -> bool:
        if self.ror and other.ror:
            return self.ror == other.ror
        elif self.isni and other.isni:
            return self.isni == other.isni
        else:
            return self.name == other.name

    def __hash__(self) -> int:
        if self.ror:
            return hash(self.ror)
        elif self.isni:
            return hash(self.isni)
        else:
            return hash(self.name)

    def __str__(self) -> str:
        return (f"Institution: {self.name} - identifiers: {self.ror} (ROR), "
                f"{self.isni} (ISNI)")

    # TODO - reevaluate rank calculation & rank values
    def calculate_internal_rank(self, researcher: Researcher) -> float:
        self.internal_rank = 0

        if self.ror:
            self.internal_rank += self._ror_rank_value

        if self.isni:
            self.internal_rank += self._isni_rank_value

        if self.name:
            self.internal_rank += self._name_rank_value

        return self.internal_rank
