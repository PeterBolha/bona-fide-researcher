"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
from abc import ABC, abstractmethod
from typing import List

from models.researcher import Researcher
from models.search_results.search_result import SearchResult
from models.search_results.unified_search_result import UnifiedSearchResult


class BaseVerificationModule(ABC):
    def __init__(self, verbose: bool = False, data_source_name: str = "?"):
        self.verbose = verbose
        self.data_source_name = data_source_name

    @abstractmethod
    def get_unified_search_results(self, search_results: List[SearchResult]) \
            -> List[UnifiedSearchResult]:
        pass

    @abstractmethod
    def verify(self, researcher: Researcher) -> List[SearchResult]:
        """
        Extract info about the researcher in a module-specific way and print
        the output.
        :param researcher: researcher to verify
        """
        pass
