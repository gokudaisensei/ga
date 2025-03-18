from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class SchedulingConfig:
    """
    Configuration settings for the timetable scheduling genetic algorithm.

    Provides centralized control over algorithm parameters and constraints.
    """

    # Genetic Algorithm Parameters
    POPULATION_SIZE: int = 200
    MAX_GENERATIONS: int = 100
    CROSSOVER_PROBABILITY: float = 0.7
    MUTATION_PROBABILITY: float = 0.3

    # Constraint Weights
    HARD_CONSTRAINT_PENALTY: int = 1000
    SOFT_CONSTRAINT_PENALTY: int = 1

    # Timetable Constraints
    DAYS_OF_WEEK: List[str] = field(
        default_factory=lambda: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )

    PERIODS_PER_DAY: List[int] = field(default_factory=lambda: list(range(1, 7)))

    # Repair and Mutation Configuration
    MUTATION_INDIVIDUAL_PROBABILITY: float = 0.1

    # Visualization Settings
    TABULATE_FORMAT: str = "grid"

    # Soft Constraint Preferences
    TEACHER_PREFERENCE_WEIGHT: int = 1
    HOME_ROOM_PREFERENCE_WEIGHT: int = 1

    # Logging and Debugging
    RANDOM_SEED: int = 42
    VERBOSE: bool = True

    # Advanced Constraints
    MAX_COURSES_PER_DAY: int = 3
    MAX_TEACHER_DAILY_LOAD: int = 4

    # Allowed Time Constraints
    ALLOWED_TEACHING_TIMES: List[Tuple[str, int]] = field(
        default_factory=lambda: [
            ("Monday", 1),
            ("Monday", 2),
            ("Monday", 3),
            ("Tuesday", 1),
            ("Tuesday", 2),
            ("Tuesday", 3),
            ("Wednesday", 1),
            ("Wednesday", 2),
            ("Wednesday", 3),
            ("Thursday", 1),
            ("Thursday", 2),
            ("Thursday", 3),
            ("Friday", 1),
            ("Friday", 2),
            ("Friday", 3),
        ]
    )

    @classmethod
    def validate_config(cls) -> None:
        """
        Validate configuration settings to ensure consistency.

        Raises:
            ValueError: If configuration settings are invalid.
        """
        if len(cls.DAYS_OF_WEEK) == 0:
            raise ValueError("At least one day must be specified")

        if len(cls.PERIODS_PER_DAY) == 0:
            raise ValueError("At least one period must be specified")

        if not (0 <= cls.CROSSOVER_PROBABILITY <= 1):
            raise ValueError("Crossover probability must be between 0 and 1")

        if not (0 <= cls.MUTATION_PROBABILITY <= 1):
            raise ValueError("Mutation probability must be between 0 and 1")

        if cls.POPULATION_SIZE < 10:
            raise ValueError("Population size must be at least 10")

        if cls.MAX_GENERATIONS < 1:
            raise ValueError("Maximum generations must be at least 1")

    @classmethod
    def get_configuration(cls) -> dict:
        """
        Retrieve a dictionary of current configuration settings.

        Returns:
            dict: A dictionary of configuration settings
        """
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith("__") and not callable(value)
        }
