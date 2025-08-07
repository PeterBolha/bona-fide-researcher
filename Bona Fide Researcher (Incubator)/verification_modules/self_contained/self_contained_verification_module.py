from abc import ABC, abstractmethod

from models.researcher import Researcher


# Base class for verification modules that do not return any values that
# would need to be integrated with others
class SelfContainedVerificationModule(ABC):
    def __init__(self, verbose: bool = False, is_active: bool = True,
                 data_source_name: str = "?", api_name: str = "other"):
        self.verbose = verbose
        self.is_active = is_active
        self.data_source_name = data_source_name
        # how the results will be named in the API response
        self.api_name = api_name

    @abstractmethod
    def verify(self, researcher: Researcher) -> dict:
        pass