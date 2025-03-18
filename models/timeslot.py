from dataclasses import dataclass


@dataclass
class TimeSlot:
    """
    Represents a specific time slot in the timetable.

    Attributes:
        slot_id (int): Unique identifier for the time slot
        day (str): Day of the week
        period (int): Period number within the day
    """

    slot_id: int
    day: str
    period: int

    def __post_init__(self):
        """
        Validates the input data during initialization.

        Raises:
            ValueError: If the period is not a positive integer or
                        the day is not valid.
        """
        if self.period < 1:
            raise ValueError("Period must be a positive integer")

        valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
        if self.day not in valid_days:
            raise ValueError(f"Invalid day: {self.day}. Expected one of {valid_days}")
