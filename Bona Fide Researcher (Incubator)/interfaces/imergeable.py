import abc
from typing import Generic, TypeVar

T = TypeVar('T', bound='IMergeable')

class IMergeable(Generic[T]):
    @abc.abstractmethod
    def merge_with(self, other: T) -> None:
        """
        Merge an object of implementing class T with another object class of T
        :param other: object to merge with the calling object
        """
        pass