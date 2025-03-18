from dataclasses import dataclass
from typing import Optional


@dataclass
class Gene:
    """
    Represents a single gene in the timetable scheduling chromosome.

    A gene encapsulates the assignment of a course to a specific group,
    at a particular time, with a specific teacher and room.

    Attributes:
        group_id (int): Identifier of the student group
        day (str): Day of the week for the class
        period (int): Period number during the day
        timeslot_id (int): Unique identifier for the timeslot
        course_id (int): Identifier of the course
        teacher_id (int): Identifier of the assigned teacher
        room_id (int): Identifier of the assigned room
        is_fixed (bool, optional): Indicates if the gene should not be altered. Defaults to False.
    """

    group_id: int
    day: str
    period: int
    timeslot_id: int
    course_id: int
    teacher_id: int
    room_id: int
    is_fixed: Optional[bool] = False

    def __post_init__(self):
        """
        Validates the gene's attributes during initialization.

        Raises:
            ValueError: If period is not positive or day is invalid.
        """
        if self.period < 1:
            raise ValueError("Period must be a positive integer")

        valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
        if self.day not in valid_days:
            raise ValueError(f"Invalid day: {self.day}. Expected one of {valid_days}")
