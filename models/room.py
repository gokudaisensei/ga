from dataclasses import dataclass


@dataclass
class Room:
    """
    Represents a classroom or teaching space with unique identification.

    Attributes:
        room_id (int): Unique identifier for the room
        name (str): Name or number of the room
    """

    room_id: int
    name: str
