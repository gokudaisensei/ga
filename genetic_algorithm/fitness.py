from typing import List, Tuple, Dict

from .chromosome import Chromosome
from models.teacher import Teacher
from models.student_group import StudentGroup

# ------------------------------
# Hard Constraint Functions
# ------------------------------


def penalty_teacher_conflict(individual: Chromosome) -> float:
    """Penalty for a teacher assigned to more than one class at the same day and period."""
    penalty = 0
    teacher_conflicts: Dict[Tuple[int, str, int], int] = {}
    for gene in individual.genes:
        key = (gene.teacher_id, gene.day, gene.period)
        teacher_conflicts[key] = teacher_conflicts.get(key, 0) + 1
    for count in teacher_conflicts.values():
        if count > 1:
            penalty += 1000 * (count - 1)
    return penalty


def penalty_room_conflict(individual: Chromosome) -> float:
    """Penalty for a room being assigned to more than one class at the same day and period."""
    penalty = 0
    room_conflicts: Dict[Tuple[int, str, int], int] = {}
    for gene in individual.genes:
        key = (gene.room_id, gene.day, gene.period)
        room_conflicts[key] = room_conflicts.get(key, 0) + 1
    for count in room_conflicts.values():
        if count > 1:
            penalty += 1000 * (count - 1)
    return penalty


def penalty_group_conflict(individual: Chromosome) -> float:
    """Penalty for a student group having more than one lesson at the same day and period."""
    penalty = 0
    group_conflicts: Dict[Tuple[int, str, int], int] = {}
    for gene in individual.genes:
        key = (gene.group_id, gene.day, gene.period)
        group_conflicts[key] = group_conflicts.get(key, 0) + 1
    for count in group_conflicts.values():
        if count > 1:
            penalty += 1000 * (count - 1)
    return penalty


# ------------------------------
# Soft Constraint Functions
# ------------------------------


def penalty_teacher_time_preference(
    individual: Chromosome, teachers: List[Teacher]
) -> float:
    """
    Penalizes a gene if the assigned teacher is scheduled outside his/her preferred times.
    Each violation adds 1 penalty point.
    """
    penalty = 0
    for gene in individual.genes:
        teacher_pref = next(
            (t.preferred_times for t in teachers if t.teacher_id == gene.teacher_id), []
        )
        if (gene.day, gene.period) not in teacher_pref:
            penalty += 1
    return penalty


def penalty_teacher_workload_balance(individual: Chromosome) -> float:
    """
    Penalizes imbalanced teaching assignments.
    The penalty is the sum of the absolute differences between each teacher's load
    and the average load.
    """
    penalty = 0
    teacher_assignments: Dict[int, int] = {}
    for gene in individual.genes:
        teacher_assignments.setdefault(gene.teacher_id, 0)
        teacher_assignments[gene.teacher_id] += 1

    if teacher_assignments:
        avg_load = sum(teacher_assignments.values()) / len(teacher_assignments)
        for load in teacher_assignments.values():
            penalty += abs(load - avg_load)
    return penalty


def penalty_group_home_room(
    individual: Chromosome, groups: List[StudentGroup]
) -> float:
    """
    Penalizes the timetable if a group is scheduled in a room other than its designated home room.
    Each violation adds 1 penalty point.
    """
    penalty = 0
    for gene in individual.genes:
        group_home = next(
            (g.home_room for g in groups if g.group_id == gene.group_id), None
        )
        if group_home is not None and gene.room_id != group_home:
            penalty += 1
    return penalty


# ------------------------------
# Additional Constraint Functions
# ------------------------------


def penalty_subject_distribution(individual: Chromosome) -> float:
    """
    Encourages teachers to have a more distributed schedule by adding a small penalty
    for consecutive classes (e.g., lessons scheduled in consecutive periods).
    """
    penalty = 0
    teacher_schedule: Dict[int, Dict[str, List[int]]] = {}
    for gene in individual.genes:
        teacher_schedule.setdefault(gene.teacher_id, {}).setdefault(
            gene.day, []
        ).append(gene.period)
    for day_dict in teacher_schedule.values():
        for periods in day_dict.values():
            periods.sort()
            # Add a small penalty for each consecutive period assignment.
            for i in range(1, len(periods)):
                if periods[i] == periods[i - 1] + 1:
                    penalty += 0.5
    return penalty


def penalty_group_schedule_gap(
    individual: Chromosome, groups: List[StudentGroup]
) -> float:
    """
    Encourages a compact schedule for student groups.
    For each group, if there is a gap between lessons in a day, add a small penalty per gap.
    """
    penalty = 0
    timetable = (
        individual.to_timetable()
    )  # Assumes Chromosome has a to_timetable() method.
    for group in groups:
        group_schedule = timetable.get(group.group_id, {})
        for lessons in group_schedule.values():
            periods = sorted(gene.period for gene in lessons)
            if periods:
                expected_slots = max(periods) - min(periods) + 1
                actual_slots = len(periods)
                gap = expected_slots - actual_slots
                penalty += gap * 0.5
    return penalty


# ------------------------------
# New Additional Constraint Functions
# ------------------------------


def penalty_teacher_same_subject_across_groups(individual: Chromosome) -> float:
    """
    Penalizes a teacher if they are assigned the same subject (course) for different student groups.
    For each teacher-course pair, if the teacher is teaching that subject to more than one group,
    add a penalty for each additional group.
    """
    penalty = 0
    teacher_course_groups: Dict[Tuple[int, int], set] = {}
    for gene in individual.genes:
        key = (gene.teacher_id, gene.course_id)
        teacher_course_groups.setdefault(key, set()).add(gene.group_id)
    for groups_set in teacher_course_groups.values():
        if len(groups_set) > 1:
            penalty += 1000 * (len(groups_set) - 1)
    return penalty


def penalty_teacher_multiple_first_periods(individual: Chromosome) -> float:
    """
    Penalizes a teacher if they are scheduled for more than one class in the first period
    across all student groups.
    """
    penalty = 0
    teacher_first_periods: Dict[int, int] = {}
    for gene in individual.genes:
        if gene.period == 1:
            teacher_first_periods[gene.teacher_id] = (
                teacher_first_periods.get(gene.teacher_id, 0) + 1
            )
    for count in teacher_first_periods.values():
        if count > 1:
            penalty += 1000 * (count - 1)
    return penalty


# ------------------------------
# Main Evaluation Function
# ------------------------------


def evaluate_timetable(
    individual: Chromosome, teachers: List[Teacher], groups: List[StudentGroup]
) -> Tuple[float]:
    """
    Evaluates the fitness of a timetable chromosome by applying various constraints.

    Hard constraints:
      - Teacher conflicts
      - Room conflicts
      - Group conflicts

    Soft constraints:
      - Teacher time preferences
      - Teacher workload balance
      - Group home room preferences

    Additional soft constraints:
      - Subject distribution (avoid consecutive lessons)
      - Group schedule gaps

    Additional hard constraints:
      - A teacher should not teach the same subject for different groups.
      - A teacher should not have more than one class in the first period.

    Lower penalty indicates a better solution.

    Returns:
        Tuple[float]: Total penalty value (lower is better)
    """
    total_penalty = 0

    # Hard constraints
    total_penalty += penalty_teacher_conflict(individual)
    total_penalty += penalty_room_conflict(individual)
    total_penalty += penalty_group_conflict(individual)

    # Soft constraints
    total_penalty += penalty_teacher_time_preference(individual, teachers)
    total_penalty += penalty_teacher_workload_balance(individual)
    total_penalty += penalty_group_home_room(individual, groups)

    # Additional soft constraints
    total_penalty += penalty_subject_distribution(individual)
    total_penalty += penalty_group_schedule_gap(individual, groups)

    # Additional hard constraints
    total_penalty += penalty_teacher_same_subject_across_groups(individual)
    total_penalty += penalty_teacher_multiple_first_periods(individual)

    return (total_penalty,)
