from dataclasses import dataclass, field
from typing import List, Dict
from tabulate import tabulate

from .gene import Gene


@dataclass
class Chromosome:
    """
    Represents a complete timetable solution composed of multiple genes.

    Provides methods for manipulating and analyzing the timetable.

    Attributes:
        genes (List[Gene]): List of genes representing the timetable
    """

    genes: List[Gene] = field(default_factory=list)

    def add_gene(self, gene: Gene) -> None:
        """
        Adds a gene to the chromosome.

        Args:
            gene (Gene): Gene to be added to the chromosome
        """
        self.genes.append(gene)

    def to_timetable(self) -> Dict[int, Dict[str, List[Gene]]]:
        """
        Organizes genes by group and day.

        Returns:
            Dict[int, Dict[str, List[Gene]]]: Organized timetable
        """
        timetable: Dict[int, Dict[str, List[Gene]]] = {}
        for gene in self.genes:
            timetable.setdefault(gene.group_id, {}).setdefault(gene.day, []).append(
                gene
            )

        for group in timetable:
            for day in timetable[group]:
                timetable[group][day].sort(key=lambda g: g.period)

        return timetable

    def pretty_print(self) -> None:
        """
        Prints a formatted timetable using tabulate.
        """
        timetable = self.to_timetable()
        for group_id, days in sorted(timetable.items()):
            print(f"\nTimetable for Group {group_id}:")
            headers = ["Day", "Period", "Course", "Teacher", "Room"]
            table_data = []
            for day, genes in sorted(days.items()):
                for gene in genes:
                    table_data.append(
                        [
                            day,
                            gene.period,
                            gene.course_id,
                            gene.teacher_id,
                            gene.room_id,
                        ]
                    )
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def __str__(self) -> str:
        """
        Generates a string representation of the timetable.

        Returns:
            str: Formatted timetable string
        """
        timetable = self.to_timetable()
        output = ""
        for group_id, days in sorted(timetable.items()):
            output += f"Group {group_id} Timetable:\n"
            for day, genes in sorted(days.items()):
                lessons = ", ".join(
                    f"P{gene.period}: C{gene.course_id} T{gene.teacher_id} R{gene.room_id}"
                    for gene in genes
                )
                output += f"  {day}: {lessons}\n"
            output += "\n"
        return output

    # Sequence Interface Methods for DEAP compatibility
    def __len__(self):
        return len(self.genes)

    def __getitem__(self, index):
        return self.genes[index]

    def __setitem__(self, index, value):
        self.genes[index] = value

    def __iter__(self):
        return iter(self.genes)
