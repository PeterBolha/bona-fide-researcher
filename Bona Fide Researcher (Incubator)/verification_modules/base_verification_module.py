from abc import ABC, abstractmethod

from models.researcher import Researcher


class BaseVerificationModule(ABC):
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    @abstractmethod
    def verify(self, researcher: Researcher) -> None:
        """
        Extract info about the researcher in a module-specific way and print the output.
        :param researcher: researcher to verify
        """
        pass