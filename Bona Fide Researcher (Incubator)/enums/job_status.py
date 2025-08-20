"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
from enum import Enum


class JobStatus(Enum):
    RUNNING = 1,
    FINISHED_SUCCESS = 2,
    FINISHED_ERROR = 3,
    NOT_FOUND = 4