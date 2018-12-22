"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """

    # max_floor: int
    # num_people: int

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        person_dict = {}
        for floor in range(1, self.max_floor + 1):
            person_dict[floor] = []
        for person in range(self.num_people):
            person = Person(random.sample(range(1, self.max_floor + 1), 1)[0],
                            random.sample(range(1, self.max_floor + 1), 1)[0])
            while person.start == person.target:
                person.target = \
                    random.sample(range(1, self.max_floor + 1), 1)[0]
            person_dict[person.start].append(person)
        return person_dict


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.
    Private attributes:
    _arrivals: a dictionary with round numbers mapping to another
               dictionary that maps floor number to a list of people who should
               be generated on that floor. Type: dict[int:dict[int:list]]
    """
    _arrivals: dict

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        self._arrivals = {}
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                # convert strings to ints
                # set var round_num
                round_num = int(line.pop(0))
                self._arrivals[round_num] = {}
                while len(line) > 0:
                    person = Person(int(line.pop(0)), int(line.pop(0)))

                    if person.start not in self._arrivals[round_num]:
                        self._arrivals[round_num][person.start] = []
                    self._arrivals[round_num][person.start].append(person)

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """

        if round_num in self._arrivals:
            return self._arrivals[round_num]
        else:
            return {}

###############################################################################
# Elevator moving algorithms
###############################################################################


class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    # elevators: List[Elevator]
    # waiting: Dict[int, List[Person]]
    # max_floor: int

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """

        directions = []
        for elevator in elevators:
            if elevator.floor == 1:
                directions.append(random.choice([Direction.STAY, Direction.UP]))
            elif elevator.floor == max_floor:
                directions.append(random.choice([Direction.DOWN,
                                                 Direction.STAY]))
            else:
                directions.append(random.choice([Direction.DOWN, Direction.STAY,
                                                 Direction.UP]))
        return directions


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        # """
        directions = []

        for elevator in elevators:
            if len(elevator.passengers) == 0:
                floors = []
                for floor in waiting:
                    for person in waiting[floor]:
                        floors.append(person.start)
                if len(floors) > 0:
                    if min(floors) < elevator.floor:
                        directions.append(Direction.DOWN)
                    elif min(floors) > elevator.floor:
                        directions.append(Direction.UP)
                    else:
                        directions.append(Direction.STAY)

            elif len(elevator.passengers) > 0:
                if elevator.floor > elevator.passengers[0].target:
                    directions.append(Direction.DOWN)
                elif elevator.floor < elevator.passengers[0].target:
                    directions.append(Direction.UP)
                else:
                    directions.append(Direction.STAY)

        return directions


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        directions = []
        for elevator in elevators:

            # if the elevator is empty
            if len(elevator.passengers) == 0:
                floors = []
                distances = []
                for floor in waiting:
                    if len(waiting[floor]) > 0:
                        floors.append(floor)
                        distances.append(abs(floor - elevator.floor))
                if len(distances) > 0:
                    closest_index = distances.index(min(distances))
                    closest_floor = floors[closest_index]
                    if closest_floor > elevator.floor:
                        directions.append(Direction.UP)
                    elif closest_floor < elevator.floor:
                        directions.append(Direction.DOWN)
                    else:
                        directions.append(Direction.STAY)

            # if the elevator has passengers
            elif len(elevator.passengers) > 0:
                targets = []
                distances = []
                for passenger in elevator.passengers:
                    targets.append(passenger.target)
                    distances.append(abs(elevator.floor - passenger.target))
                closest_index = distances.index(min(distances))
                closest_floor = targets[closest_index]
                if closest_floor > elevator.floor:
                    directions.append(Direction.UP)
                elif closest_floor < elevator.floor:
                    directions.append(Direction.DOWN)
                else:
                    directions.append(Direction.STAY)

        return directions


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201'],
        'max-attributes': 12
    })
