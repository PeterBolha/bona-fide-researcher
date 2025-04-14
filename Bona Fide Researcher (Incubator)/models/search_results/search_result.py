import abc

from models.researcher import Researcher


class SearchResult:
    def __init__(self, internal_rank: float = 0) -> None:
        self.internal_rank = internal_rank

    def __lt__(self, other):  # Defines sorting order (ascending by internal rank)
        return self.internal_rank < other.internal_rank

    def __eq__(self, other):  # Needed for full sorting support
        return self.internal_rank == other.internal_rank

    @abc.abstractmethod
    def print(self, verbose: bool = False) -> None:
        pass

    @abc.abstractmethod
    def calculate_internal_rank(self, researcher: Researcher) -> None:
        pass

