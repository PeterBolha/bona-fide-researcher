"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
import abc

from abstracts.rankable import Rankable
from models.researcher import Researcher


class SearchResult(Rankable):
    def __init__(self, internal_rank: float = 0) -> None:
        super().__init__(internal_rank)

    @abc.abstractmethod
    def print(self, verbose: bool = False) -> None:
        pass

    @abc.abstractmethod
    def calculate_internal_rank(self, researcher: Researcher) -> float:
        pass

