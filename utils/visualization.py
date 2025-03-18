from typing import List, Optional
from tabulate import tabulate

from genetic_algorithm.chromosome import Chromosome
from models.student_group import StudentGroup


class TimetableVisualizer:
    """
    Utility class for visualizing timetables in various formats.
    """

    @classmethod
    def visualize_grid(
        cls,
        chromosome: Chromosome,
        group_id: int,
        days: Optional[List[str]] = None,
        periods: Optional[List[int]] = None,
    ) -> None:
        """
        Visualizes the timetable for a given student group in a grid format.

        Args:
            chromosome (Chromosome): Chromosome containing the timetable
            group_id (int): Identifier of the student group
            days (Optional[List[str]], optional): Days to display.
                Defaults to standard school week.
            periods (Optional[List[int]], optional): Periods to display.
                Defaults to periods 1-3.
        """
        # Default values if not provided
        days = days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        periods = periods or [1, 2, 3, 4, 5, 6]

        # Get timetable for specific group
        timetable = chromosome.to_timetable()
        group_timetable = timetable.get(group_id, {})

        # Prepare table headers
        headers = ["Day/Period"] + [f"Period {p}" for p in periods]
        table = []

        for day in days:
            row = [day]
            day_genes = group_timetable.get(day, [])

            # Create mapping from period to gene
            period_to_gene = {gene.period: gene for gene in day_genes}

            for p in periods:
                if p in period_to_gene:
                    gene = period_to_gene[p]
                    cell_content = (
                        f"C{gene.course_id} T{gene.teacher_id} R{gene.room_id}"
                    )
                else:
                    cell_content = "-"
                row.append(cell_content)

            table.append(row)

        print(tabulate(table, headers=headers, tablefmt="grid"))

    @classmethod
    def text_summary(cls, chromosome: Chromosome, groups: List[StudentGroup]) -> None:
        """
        Generates a text summary of the timetable for all groups.

        Args:
            chromosome (Chromosome): Chromosome containing the timetable
            groups (List[StudentGroup]): List of student groups
        """
        for group in groups:
            print(f"\n===== Timetable for {group.name} (ID: {group.group_id}) =====")

            timetable = chromosome.to_timetable().get(group.group_id, {})

            for day, genes in sorted(timetable.items()):
                print(f"\n{day}:")
                for gene in sorted(genes, key=lambda g: g.period):
                    print(
                        f"  Period {gene.period}: "
                        f"Course {gene.course_id}, "
                        f"Teacher {gene.teacher_id}, "
                        f"Room {gene.room_id}"
                    )

    @classmethod
    def conflict_analysis(cls, chromosome: Chromosome) -> None:
        """
        Analyzes and reports potential conflicts in the timetable.

        Args:
            chromosome (Chromosome): Chromosome to analyze
        """
        teacher_conflicts = {}
        room_conflicts = {}
        group_conflicts = {}

        for gene in chromosome.genes:
            # Track teacher conflicts
            teacher_key = (gene.teacher_id, gene.day, gene.period)
            teacher_conflicts[teacher_key] = teacher_conflicts.get(teacher_key, 0) + 1

            # Track room conflicts
            room_key = (gene.room_id, gene.day, gene.period)
            room_conflicts[room_key] = room_conflicts.get(room_key, 0) + 1

            # Track group conflicts
            group_key = (gene.group_id, gene.day, gene.period)
            group_conflicts[group_key] = group_conflicts.get(group_key, 0) + 1

        print("\n=== Conflict Analysis ===")

        # Report teacher conflicts
        teacher_conflicts = {k: v for k, v in teacher_conflicts.items() if v > 1}
        if teacher_conflicts:
            print("\nTeacher Conflicts:")
            for (teacher_id, day, period), count in teacher_conflicts.items():
                print(
                    f"  Teacher {teacher_id} overbooked on {day}, Period {period}: {count} assignments"
                )

        # Report room conflicts
        room_conflicts = {k: v for k, v in room_conflicts.items() if v > 1}
        if room_conflicts:
            print("\nRoom Conflicts:")
            for (room_id, day, period), count in room_conflicts.items():
                print(
                    f"  Room {room_id} overbooked on {day}, Period {period}: {count} assignments"
                )

        # Report group conflicts
        group_conflicts = {k: v for k, v in group_conflicts.items() if v > 1}
        if group_conflicts:
            print("\nGroup Conflicts:")
            for (group_id, day, period), count in group_conflicts.items():
                print(
                    f"  Group {group_id} double-booked on {day}, Period {period}: {count} assignments"
                )
