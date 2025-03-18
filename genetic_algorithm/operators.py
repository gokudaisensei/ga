import random
from typing import List, Tuple

from .chromosome import Chromosome
from models.teacher import Teacher
from models.room import Room
from models.course import Course
from models.timeslot import TimeSlot


def crossover(ind1: Chromosome, ind2: Chromosome) -> Tuple[Chromosome, Chromosome]:
    """
    Perform single-point crossover on two chromosomes.

    Args:
        ind1 (Chromosome): First parent chromosome
        ind2 (Chromosome): Second parent chromosome

    Returns:
        Tuple[Chromosome, Chromosome]: Offspring chromosomes after crossover
    """
    size = len(ind1.genes)
    if size < 2:
        return ind1, ind2

    cxpoint = random.randint(1, size - 1)
    ind1.genes[cxpoint:], ind2.genes[cxpoint:] = (
        ind2.genes[cxpoint:],
        ind1.genes[cxpoint:],
    )
    return ind1, ind2


def mutation(
    individual: Chromosome,
    teachers: List[Teacher],
    rooms: List[Room],
    courses: List[Course],
    timeslots: List[TimeSlot],
    indpb: float = 0.1,
) -> Tuple[Chromosome]:
    """
    Perform mutation on a chromosome with given probability.

    Args:
        individual (Chromosome): Chromosome to mutate
        teachers (List[Teacher]): Available teachers
        rooms (List[Room]): Available rooms
        courses (List[Course]): Available courses
        timeslots (List[TimeSlot]): Available timeslots
        indpb (float, optional): Mutation probability. Defaults to 0.1.

    Returns:
        Tuple[Chromosome]: Mutated chromosome
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = [1, 2, 3]
    timeslot_map = {(ts.day, ts.period): ts.slot_id for ts in timeslots}

    for gene in individual.genes:
        if random.random() < indpb:
            gene.teacher_id = random.choice(teachers).teacher_id
        if random.random() < indpb:
            gene.course_id = random.choice(courses).course_id
        if random.random() < indpb:
            gene.room_id = random.choice(rooms).room_id
        if random.random() < indpb:
            gene.day = random.choice(days)
            gene.period = random.choice(periods)
            gene.timeslot_id = timeslot_map[(gene.day, gene.period)]

    return (individual,)
