import random
from typing import List, Dict, Tuple

from models.teacher import Teacher
from models.room import Room
from genetic_algorithm.chromosome import Chromosome


class RepairOperator:
    """
    Utility class for repairing timetable chromosomes by resolving
    conflicts and applying heuristics.
    """

    @classmethod
    def repair_timetable(
        cls, individual: Chromosome, teachers: List[Teacher], rooms: List[Room]
    ) -> Chromosome:
        """
        Apply repair heuristics to resolve conflicts in the timetable.

        Args:
            individual (Chromosome): Chromosome to be repaired
            teachers (List[Teacher]): Available teachers
            rooms (List[Room]): Available rooms

        Returns:
            Chromosome: Repaired chromosome
        """
        # Repair strategies applied in sequence
        individual = cls._resolve_teacher_conflicts(individual, teachers)
        individual = cls._resolve_room_conflicts(individual, rooms)
        individual = cls._resolve_group_conflicts(individual)

        return individual

    @classmethod
    def _resolve_teacher_conflicts(
        cls, individual: Chromosome, teachers: List[Teacher]
    ) -> Chromosome:
        """
        Resolve teacher scheduling conflicts.

        Args:
            individual (Chromosome): Chromosome to repair
            teachers (List[Teacher]): Available teachers

        Returns:
            Chromosome: Chromosome with teacher conflicts resolved
        """
        teacher_schedule: Dict[Tuple[str, int], List[int]] = {}
        teacher_load: Dict[int, int] = {t.teacher_id: 0 for t in teachers}
        teacher_preferences: Dict[int, List[Tuple[str, int]]] = {
            t.teacher_id: t.preferred_times for t in teachers
        }

        for gene in individual.genes:
            key = (gene.day, gene.period)
            teacher_schedule.setdefault(key, [])

            if gene.teacher_id in teacher_schedule[key]:
                # Find alternative teachers
                available_teachers = [
                    t.teacher_id
                    for t in teachers
                    if t.teacher_id not in teacher_schedule[key]
                ]

                if available_teachers:
                    # Prioritize teachers with preferred times
                    preferred_available = [
                        tid
                        for tid in available_teachers
                        if key in teacher_preferences.get(tid, [])
                    ]

                    # Choose teacher with least load
                    best_teacher = min(
                        preferred_available or available_teachers,
                        key=lambda tid: teacher_load[tid],
                    )

                    gene.teacher_id = best_teacher
                    teacher_load[best_teacher] += 1

            teacher_schedule[key].append(gene.teacher_id)

        return individual

    @classmethod
    def _resolve_room_conflicts(
        cls, individual: Chromosome, rooms: List[Room]
    ) -> Chromosome:
        """
        Resolve room scheduling conflicts.

        Args:
            individual (Chromosome): Chromosome to repair
            rooms (List[Room]): Available rooms

        Returns:
            Chromosome: Chromosome with room conflicts resolved
        """
        room_schedule: Dict[Tuple[str, int], List[int]] = {}
        room_usage: Dict[int, int] = {r.room_id: 0 for r in rooms}

        for gene in individual.genes:
            key = (gene.day, gene.period)
            room_schedule.setdefault(key, [])

            if gene.room_id in room_schedule[key]:
                # Find alternative rooms
                available_rooms = [
                    r.room_id for r in rooms if r.room_id not in room_schedule[key]
                ]

                if available_rooms:
                    # Choose room with least usage
                    best_room = min(available_rooms, key=lambda rid: room_usage[rid])

                    gene.room_id = best_room
                    room_usage[best_room] += 1

            room_schedule[key].append(gene.room_id)

        return individual

    @classmethod
    def _resolve_group_conflicts(cls, individual: Chromosome) -> Chromosome:
        """
        Resolve student group scheduling conflicts.

        Args:
            individual (Chromosome): Chromosome to repair

        Returns:
            Chromosome: Chromosome with group conflicts resolved
        """
        group_schedule: Dict[Tuple[int, str, int], bool] = {}

        for gene in individual.genes:
            key = (gene.group_id, gene.day, gene.period)

            if key in group_schedule:
                # If conflict exists, randomly change course
                gene.course_id = random.randint(
                    1, 3
                )  # Assumes courses are numbered 1-3

            group_schedule[key] = True

        return individual
