from rapidfuzz import fuzz

from abstracts.rankable import Rankable
from models.researcher import Researcher


class Institution(Rankable):
    def __init__(self, name: str, ror: str = None, isni: str = None) -> None:
        super().__init__()
        self.name = name
        self._name_rank_value_presence_multiplier = 0.1

        # Research Organization Registry ID
        self.ror = ror
        self._ror_rank_value_presence_multiplier = 0.1
        self._ror_rank_value_match_multiplier = 1

        # International Standard Name Identifier
        self.isni = isni
        self._isni_rank_value_presence_multiplier = 0.1
        self._isni_rank_value_match_multiplier = 1

        self.rank_calculation_base_value = 100
        self.has_perfect_match = False


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

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ror": self.ror,
            "isni": self.isni,
        }

    # TODO - reevaluate rank calculation & rank values
    def calculate_internal_rank(self, researcher: Researcher) -> float:
        self.internal_rank = 0
        target_affiliation = researcher.affiliation

        if self.ror:
            if self.ror == target_affiliation:
                self.has_perfect_match = True
                self.internal_rank += (
                        self._ror_rank_value_match_multiplier *
                        self.rank_calculation_base_value)
            else:
                self.internal_rank += (
                        self._ror_rank_value_presence_multiplier *
                        self.rank_calculation_base_value)
        if self.isni:
            if self.isni == target_affiliation:
                self.has_perfect_match = True
                self.internal_rank += (
                        self._isni_rank_value_match_multiplier *
                        self.rank_calculation_base_value)
            else:
                self.internal_rank += (
                        self._isni_rank_value_presence_multiplier *
                        self.rank_calculation_base_value)

        if self.name:
            base_rank = (self._name_rank_value_presence_multiplier *
                         self.rank_calculation_base_value)
            match_rank = fuzz.ratio(self.name, researcher.affiliation)
            if match_rank == 100:
                self.has_perfect_match = True

            self.internal_rank += max(base_rank, match_rank)

        return self.internal_rank
