"""Assignment 1 - Simulation

=== CSC148 Fall 2018 ===

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    Public
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)

    Private
    _elevator_capacity: capacity of elevator
    _num_elevators: number of elevators in simulation instance
    _num_rounds: number of rounds
    _num_people_per_round: number of people generated every round
    _people_completed: number of people who reached their target floor
    _total_people: total number or people generated
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]

    _elevator_capacity: int
    _num_elevators: int
    _num_rounds: int
    _num_people_per_round: int
    _people_completed: []
    _total_people: int

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        self.moving_algorithm = config['moving_algorithm']
        self.arrival_generator = config['arrival_generator']
        self._num_elevators = config['num_elevators']
        # Initialize elevators
        self.elevators = []
        count = self._num_elevators
        while count > 0:
            self.elevators.append(Elevator(config["elevator_capacity"]))
            count -= 1
        self.num_floors = config['num_floors']
        self.waiting = {}
        for floor in range(1, self.num_floors + 1):
            self.waiting[floor] = []
        self._num_people_per_round = config['num_people_per_round']
        self._people_completed = []
        self._num_rounds = 0
        self._total_people = 0

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.visualizer = Visualizer(self.elevators,  # should be self.elevators
                                     self.num_floors,
                                     # should be self.num_floors
                                     config['visualize'])

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        self._num_rounds = num_rounds

        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)

            # update each person's wait_time attribute for all persons in
            # self.waiting
            for floor in self.waiting:
                for person in self.waiting[floor]:
                    person.wait_time += 1

            for elevator in self.elevators:
                for passenger in elevator.passengers:
                    passenger.wait_time += 1

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals.
        Update the waiting instance attribute of the simulation, as well as call
        the Visualizer.show_arrivals method appropriately to actually show the
        new arrivals in the Pygame window
        """
        # if self.waiting == {}:
        #     for floor in range(1, self.num_floors + 1):
        #         self.waiting[floor] = []

        # Generate new arrivals
        new_arrivals = self.arrival_generator.generate(round_num)

        if new_arrivals != {}:

            for floor in range(1, self.num_floors + 1):
                if floor in new_arrivals and floor in self.waiting:
                    for person in new_arrivals[floor]:
                        self.waiting[floor].append(person)
                        self._total_people += 1

            # Visualize new arrivals
            self.visualizer.show_arrivals(new_arrivals)
            # print(self.waiting)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for elevator in self.elevators:
            for person in elevator.passengers:
                if person.target == elevator.floor:
                    self._people_completed.append(person.wait_time)
                    elevator.passengers.remove(person)
                    self.visualizer.show_disembarking(person, elevator)

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for elevator in self.elevators:
            for person in self.waiting[elevator.floor]:
                if elevator.fullness() < 1:
                    elevator.passengers.append(person)
                    self.waiting[elevator.floor] = \
                        self.waiting[elevator.floor][1:]
                    self.visualizer.show_boarding(person, elevator)

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        directions = self.moving_algorithm.move_elevators(self.elevators,
                                                          self.waiting,
                                                          self.num_floors)
        for index in range(len(directions)):
            if directions[index] == Direction.DOWN:
                self.elevators[index].floor -= 1
            elif directions[index] == Direction.UP:
                self.elevators[index].floor += 1

        self.visualizer.show_elevator_moves(self.elevators, directions)

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        if len(self._people_completed) == 0:
            max_time = -1
            min_time = -1
            avg_time = -1
        elif len(self._people_completed) > 0:
            max_time = max(self._people_completed)
            min_time = min(self._people_completed)
            avg_time = str(sum(self._people_completed) /
                           len(self._people_completed))
            avg_time = int(avg_time[0])

        return {
            'num_iterations': self._num_rounds,
            'total_people': self._total_people,
            'people_completed': len(self._people_completed),
            'max_time': max_time,
            'min_time': min_time,
            'avg_time': avg_time
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'num_elevators': 3,
        'elevator_capacity': 3,
        'num_people_per_round': 4,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.FileArrivals(6, 'sample_arrivals.csv'),
        'moving_algorithm': algorithms.ShortSighted(),
        'visualize': True
    }
    sim = Simulation(config)
    stats = sim.run(9)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4,
        'disable': ['R0201'],
        'max-attributes': 12
    })
