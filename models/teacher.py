from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Teacher:
    """
    Represents a teacher with unique identification and preferred teaching times.

    Attributes:
        teacher_id (int): Unique identifier for the teacher
        name (str): Name of the teacher
        preferred_times (List[Tuple[str, int]]): List of preferred teaching times
            represented as (day, period) tuples
    """

    teacher_id: int
    name: str
    preferred_times: List[Tuple[str, int]]
