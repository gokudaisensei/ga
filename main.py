import random

from deap import base, creator, tools

from genetic_algorithm.chromosome import Chromosome
from genetic_algorithm.operators import crossover, mutation
from genetic_algorithm.fitness import evaluate_timetable

from utils.data_generator import DataGenerator
from utils.repair_operator import RepairOperator
from utils.visualization import TimetableVisualizer

from config.settings import SchedulingConfig


class TimetableScheduler:
    """
    Main application class for timetable scheduling using genetic algorithm.

    Orchestrates the entire scheduling process from data generation
    to final timetable creation.
    """

    def __init__(self, config: SchedulingConfig = SchedulingConfig()):
        """
        Initialize the timetable scheduler.

        Args:
            config (SchedulingConfig, optional): Configuration settings.
                Defaults to default configuration.
        """
        self.config = config

        # Set random seed for reproducibility
        random.seed(config.RANDOM_SEED)

        # DEAP setup
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", Chromosome, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()

        # Prepare dataset
        self._prepare_dataset()

        # Setup genetic algorithm components
        self._setup_genetic_algorithm()

    def _prepare_dataset(self):
        """
        Generate comprehensive dataset for timetable scheduling.
        """
        (self.groups, self.courses, self.teachers, self.rooms, self.timeslots) = (
            DataGenerator.create_complete_dataset_dc()
        )

    def _setup_genetic_algorithm(self):
        """
        Configure DEAP toolbox for genetic algorithm operations.
        """

        def init_individual():
            """
            Initialize a random chromosome individual.

            Returns:
                Individual chromosome for genetic algorithm
            """
            chromosome = Chromosome()
            for group in self.groups:
                for day in self.config.DAYS_OF_WEEK:
                    for period in self.config.PERIODS_PER_DAY:
                        # Generate a random gene for each group-day-period combination
                        gene = self._generate_random_gene(group.group_id, day, period)
                        chromosome.add_gene(gene)
            return creator.Individual(chromosome.genes)

        self.toolbox.register(
            "individual", tools.initIterate, creator.Individual, init_individual
        )
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )

        # Genetic operators
        self.toolbox.register(
            "evaluate", lambda ind: evaluate_timetable(ind, self.teachers, self.groups)
        )
        self.toolbox.register("mate", crossover)
        self.toolbox.register(
            "mutate",
            lambda ind: mutation(
                ind,
                self.teachers,
                self.rooms,
                self.courses,
                self.timeslots,
                indpb=self.config.MUTATION_INDIVIDUAL_PROBABILITY,
            ),
        )
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def _generate_random_gene(self, group_id: int, day: str, period: int):
        """
        Generate a random gene for a specific group, day, and period.

        Args:
            group_id (int): Identifier of the student group
            day (str): Day of the week
            period (int): Period number

        Returns:
            Gene with randomized attributes
        """
        from genetic_algorithm.gene import Gene

        timeslot_id = next(
            ts.slot_id for ts in self.timeslots if ts.day == day and ts.period == period
        )

        return Gene(
            group_id=group_id,
            day=day,
            period=period,
            timeslot_id=timeslot_id,
            course_id=random.choice(self.courses).course_id,
            teacher_id=random.choice(self.teachers).teacher_id,
            room_id=random.choice(self.rooms).room_id,
        )

    def run(self):
        """
        Execute the genetic algorithm for timetable scheduling.

        Performs evolutionary optimization to generate an optimal timetable.
        """
        # Initialize population
        pop = self.toolbox.population(n=self.config.POPULATION_SIZE)

        # Initial repair and evaluation
        for ind in pop:
            chromosome = Chromosome(genes=ind)
            RepairOperator.repair_timetable(chromosome, self.teachers, self.rooms)
            ind.fitness.values = self.toolbox.evaluate(ind)

        # Evolutionary loop
        for gen in range(self.config.MAX_GENERATIONS):
            if self.config.VERBOSE:
                print(f"\n--- Generation {gen} ---")

            # Select offspring
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(self.toolbox.clone, offspring))

            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.config.CROSSOVER_PROBABILITY:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Mutation
            for mutant in offspring:
                if random.random() < self.config.MUTATION_PROBABILITY:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Repair and re-evaluate
            for ind in offspring:
                chromosome = Chromosome(genes=ind)
                RepairOperator.repair_timetable(chromosome, self.teachers, self.rooms)
                if not ind.fitness.valid:
                    ind.fitness.values = self.toolbox.evaluate(ind)

            # Replace population
            pop[:] = offspring

            # Track best solution
            best = min(pop, key=lambda ind: ind.fitness.values[0])
            if self.config.VERBOSE:
                print(f"Best penalty: {best.fitness.values[0]}")

        # Find and display final best solution
        final_best = min(pop, key=lambda ind: ind.fitness.values[0])
        best_chromosome = Chromosome(genes=final_best)

        print("\n=== Final Best Timetable ===")
        self.visualize_results(best_chromosome)
        return best_chromosome

    def visualize_results(self, chromosome: Chromosome):
        """
        Visualize the final timetable solution.

        Args:
            chromosome (Chromosome): Best timetable chromosome
        """
        # Grid visualization for each group
        for group in self.groups:
            print(f"\nGrid for Group {group.group_id}:")
            TimetableVisualizer.visualize_grid(chromosome, group.group_id)

        # Detailed text summary
        TimetableVisualizer.text_summary(chromosome, self.groups)

        # Conflict analysis
        TimetableVisualizer.conflict_analysis(chromosome)


def main():
    """
    Entry point for the timetable scheduling application.
    """
    # Optional: Custom configuration
    # config = SchedulingConfig(
    #     POPULATION_SIZE=100,
    #     MAX_GENERATIONS=200,
    #     VERBOSE=True
    # )

    # Initialize and run scheduler
    scheduler = TimetableScheduler()
    return scheduler.run()


if __name__ == "__main__":
    jack = main()
