from dataclasses import dataclass


@dataclass
class Course:
    """
    Represents an academic course with unique identification.

    Attributes:
        course_id (int): Unique identifier for the course
        name (str): Name of the course
    """

    course_id: int
    name: str
