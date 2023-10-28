"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2023 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.
"""
import csv
from python_ta.contracts import check_contracts

from a1_entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
@check_contracts
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    This is an abstract class, and should not be instantiated directly.
    We have started two subclasses of this class down below.

    Instance Attributes:
    - max_floor: The maximum floor number for the building.
        Generated people must not have a starting or target floor
        beyond this floor.

    Representation Invariants:
    - self.max_floor >= 2
    """
    max_floor: int

    def __init__(self, max_floor: int) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
        - max_floor >= 2
        """
        self.max_floor = max_floor

    def generate(self, round_num: int) -> dict[int, list[Person]]:
        """Return the new arrivals for the simulation at the given round.

        Order matters: if there two people with the same starting floor
        in the returned list, the person who appears first in the list
        is considered to have arrived at the floor first.

        Note: only floors with at least one new arrival should be included
        in the returned dictionary. In other words, there should not be
        any empty lists in the returned dictionary.

        Preconditions:
        - round_num >= 0
        """
        raise NotImplementedError


@check_contracts
class SingleArrivals(ArrivalGenerator):
    """An arrival generator that adds one person to floor 1 each round.

    SingleArrivals.generate algorithm description:

    - This implementation always generates exactly ONE Person per round.
    - The new Person always has a starting floor of 1.
    - At round 0, the new Person has a target floor of 2.
    - At each subsequent round, the new Person has a target floor one greater than
      the previous round, until self.max_floor is reached. At the next round, the target floor
      starts back at 2.
    - For example, if self.max_floor == 4:
        - Round 0: target floor 2
        - Round 1: target floor 3
        - Round 2: target floor 4
        - Round 3: target floor 2
        - Round 4: target floor 3
        - Round 5: target floor 4
        - Round 6: target floor 2
        - etc.
    """
    def generate(self, round_num: int) -> dict[int, list[Person]]:
        """Return the new arrivals for the simulation at the given round.

        Order matters: if there two people with the same starting floor
        in the returned list, the person who appears first in the list
        is considered to have arrived at the floor first.

        Note: only floors with at least one new arrival should be included
        in the returned dictionary. In other words, there should not be
        any empty lists in the returned dictionary.

        Preconditions:
        - round_num >= 0

        >>> my_generator = SingleArrivals(4)
        >>> my_arrivals = my_generator.generate(0)
        >>> len(my_arrivals) == 1
        True
        >>> print(my_arrivals[1])
        [Person(start=1, target=2, wait_time=0)]
        """
        # Calculate the target floor.
        # (round_num % (self.max_floor - 1)) will cycle from 0 to self.max_floor - 2
        # Adding 2 makes it cycle from 2 to self.max_floor.
        target_floor = 2 + (round_num % (self.max_floor - 1))

        # Create a new person with starting floor of 1 and the calculated target floor
        new_person = Person(1, target_floor)

        # Return a dictionary with the new person
        return {1: [new_person]}


@check_contracts
class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.

    Instance Attributes:
    - arrival_data: the arrivals parsed from the given csv file.

    Representation Invariants:
    - Every key in self.arrival_data is between 1 and self.max_floor.

    We have provided some sample CSV files under the data/ folder.
    """
    arrival_data: dict[int, list[Person]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        Preconditions:
        - <filename> refers to a valid CSV file, following the specified
          format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        self.arrival_data = {}

        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                round_num = int(line[0])
                i = 1
                while i < len(line):
                    start_floor = int(line[i])
                    target_floor = int(line[i + 1])
                    person = Person(start_floor, target_floor)
                    if round_num in self.arrival_data:
                        self.arrival_data[round_num].append(person)
                    else:
                        self.arrival_data[round_num] = [person]
                    i += 2

    def generate(self, round_num: int) -> dict[int, list[Person]]:
        """Return the new arrivals for the simulation at the given round.

        Order matters: if there two people with the same starting floor
        in the returned list, the person who appears first in the list
        is considered to have arrived at the floor first.

        Note: only floors with at least one new arrival should be included
        in the returned dictionary. In other words, there should not be
        any empty lists in the returned dictionary.

        Preconditions:
        - round_num >= 0

        >>> my_generator = FileArrivals(5, 'data/sample_arrivals.csv')
        >>> round0_arrivals = my_generator.generate(0)
        >>> len(round0_arrivals)  # Only two floors in the dictionary
        2
        >>> print(round0_arrivals[1])
        [Person(start=1, target=4, wait_time=0)]
        >>> print(round0_arrivals[5])
        [Person(start=5, target=3, wait_time=0)]
        """
        if round_num in self.arrival_data:
            return {person.start: [person] for person in self.arrival_data[round_num]}
        return {}


###############################################################################
# Elevator moving algorithms
###############################################################################
@check_contracts
class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.

    IMPORTANT: this algorithm doesn't actually move the elevators, i.e., it doesn't change
    their current floor. Instead, it only updates the target_floor attribute of each elevator
    (or leaves it unchanged). The actual moving should be done in Simulation.move_elevators.

    This is an abstract class, and should not be instantiated directly.
    We have started two subclasses of this class down below.
    """
    def update_target_floors(self,
                             elevators: list[Elevator],
                             waiting: dict[int, list[Person]],
                             max_floor: int) -> None:
        """Updates elevator target floors.

        The parameters are:
        - elevators: a list of the system's elevators
        - waiting: a dictionary mapping floor number to the list of people waiting on that floor
        - max_floor: the maximum floor number in the simulation

        Preconditions:
        - elevators, waiting, and max_floor are from the same simulation run
        """
        raise NotImplementedError


@check_contracts
class EndToEndLoop(MovingAlgorithm):
    """A moving algorithm that causes every elevator to move between the bottom and top floors.

    Algorithm description:

    - For each elevator:
        - If the elevator's current floor is 1, the target_floor is set to the max_floor.
        - If the elevator's current floor is max_floor, the target_floor is set to 1.
        - In all other cases, the elevator's target_floor is unchanged.
    - This algorithm behaves the same way for all elevators.
    - This algorithm IGNORES the passengers on the elevators, and the people
      who are waiting for an elevator.
    """

    def update_target_floors(self,
                             elevators: list[Elevator],
                             waiting: dict[int, list[Person]],
                             max_floor: int) -> None:
        """Updates elevator target floors based on the algorithm's rules."""
        for elevator in elevators:
            if elevator.current_floor == 1:
                elevator.target_floor = max_floor
            elif elevator.current_floor == max_floor:
                elevator.target_floor = 1


@check_contracts
class FurthestFloor(MovingAlgorithm):
    """A moving algorithm that chooses far-away target floors.

    Algorithm description:

    For *each* elevator:

    - *Case 1*: If the elevator has at least one passenger, set the elevator's target floor
      to be the floor that is a passenger's target floor and is the furthest away from the
      elevator's current floor.
    - *Case 2*: If the elevator has no passengers and is idle, set the elevator's target floor
      to be the floor that has at least one passenger waiting and is the furthest away from the
      elevator's current floor.
        - If there are no waiting people at all, set the elevator's target floor to the
          current floor. The elevator remains idle and does not move this round.
    - *Case 3*: If the elevator has no passengers and is not idle, do not change the target floor.

    Note: In Cases 1 and 2, if there is a tie, always pick the *lowest* floor.
    """
    def update_target_floors(self, elevators, waiting, max_floor):
        for elevator in elevators:
            # Calculate the furthest distance for both up and down directions
            floors_above = [floor for floor in range(elevator.current_floor + 1, max_floor + 1) if
                            waiting[floor]]
            floors_below = [floor for floor in range(1, elevator.current_floor) if waiting[floor]]

            if floors_above and (not floors_below or max(floors_above) - elevator.current_floor >=
                                 elevator.current_floor - min(floors_below)):
                elevator.target_floor = max(floors_above)
            elif floors_below:
                # If there are waiting floors below and they are closer
                elevator.target_floor = min(floors_below)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # Uncomment the python_ta lines below and run this module.
    # This is different that just running doctests! To run this file in PyCharm,
    # right-click in the file and select "Run a1_algorithms" or "Run File in Python Console".
    #
    # python_ta will check your work and open up your web browser to display
    # its report. For full marks, you must fix all issues reported, so that
    # you see "None!" under both "Code Errors" and "Style and Convention Errors".
    # TIP: To quickly uncomment lines in PyCharm, select the lines below and press
    # "Ctrl + /" or "⌘ + /".
    # import python_ta
    # python_ta.check_all(config={
    #     'allowed-io': ['FileArrivals.__init__'],
    #     'extra-imports': ['a1_entities', 'csv'],
    #     'max-nested-blocks': 4,
    #     'max-line-length': 100
    # })
