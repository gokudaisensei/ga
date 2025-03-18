from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentGroup:
    """
    Represents a student group with unique identification and optional home room.

    Attributes:
        group_id (int): Unique identifier for the student group
        name (str): Name of the student group
        home_room (Optional[int]): Designated home room for the group, if applicable
    """

    group_id: int
    name: str
    home_room: Optional[int] = None
