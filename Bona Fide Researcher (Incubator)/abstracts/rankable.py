"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
import abc

from models.researcher import Researcher


class Rankable:
    def __init__(self, internal_rank: float = 0) -> None:
        self.internal_rank = internal_rank

    def __lt__(self,
               other: "Rankable"):  # Defines sorting order (ascending by
        # internal rank)
        return self.internal_rank < other.internal_rank

    @abc.abstractmethod
    def calculate_internal_rank(self, researcher: Researcher) -> float:
        """
        Calculate the rank of a ranked entity and store it internally
        :returns: calculated internal rank
        :param researcher: target researcher being verified
        """
        pass
