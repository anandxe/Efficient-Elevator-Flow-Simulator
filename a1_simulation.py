"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2023 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function run_example_simulation
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
modify/remove any of the existing attributes.
"""
# You MAY import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Any
from python_ta.contracts import check_contracts

import a1_algorithms
from a1_entities import Person, Elevator
from a1_visualizer import Direction, Visualizer


@check_contracts
class Simulation:
    """The main simulation class.

    Instance Attributes:
    - arrival_generator: the algorithm used to generate new arrivals.
    - elevators: a list of the elevators in the simulation
    - moving_algorithm: the algorithm used to decide how to move elevators
    - num_floors: the number of floors
    - visualizer: the Pygame visualizer used to visualize this simulation
    - waiting: a dictionary of people waiting for an elevator, where:
        - The keys are floor numbers from 1 to num_floors, inclusive
        - Each corresponding value is the list of people waiting at that floor
          (could be an empty list)

    Representation Invariants:
    - len(self.elevators) >= 1
    - self.num_floors >= 2
    - list(self.waiting.keys()) == list(range(1, self.num_floors + 1))
    """
    arrival_generator: a1_algorithms.ArrivalGenerator
    elevators: list[Elevator]
    moving_algorithm: a1_algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: dict[int, list[Person]]

    def __init__(self,
                 config: dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration.

        Preconditions:
        - config is a dictionary in the format found on the assignment handout
        - config['num_floors'] >= 2
        - config['elevator_capacity'] >= 1
        - config['num_elevators'] >= 1

        A partial implementation has been provided to you; you'll need to finish it!
        """

        # Initialize the algorithm attributes (this is done for you)
        self.arrival_generator = config['arrival_generator']
        self.moving_algorithm = config['moving_algorithm']

        # The number of floors in the building
        self.num_floors = config['num_floors']

        # Initialize the list of elevators. Each elevator starts on the first floor
        # and has the given capacity.
        self.elevators = [Elevator(config['elevator_capacity'])
                          for elevator_index in range(config['num_elevators'])]

        # Initialize waiting list. Each floor starts with an empty list of waiting people.
        self.waiting = {floor_num: [] for floor_num in range(1, self.num_floors + 1)}

        # Now that elevators and number of floors are initialized, initialize the visualizer
        self.visualizer = Visualizer(self.elevators, self.num_floors, config['visualize'])

        # Initialize tracking attributes
        self.total_arrivals = 0
        self.completed_people = []
        self.num_rounds = 0

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> dict[str, int]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Preconditions:
        - num_rounds >= 1
        - This method is only called once for each Simulation instance
            (since we have not asked you to "reset" back to the initial simulation state
            for this assignment)
        """
        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: elevator disembarking
            self.handle_disembarking()

            # Stage 2: new arrivals
            self.generate_arrivals(i)

            # Stage 3: elevator boarding
            self.handle_boarding()

            # Stage 4: move the elevators
            self.move_elevators()

            # Stage 5: update wait times
            self.update_wait_times()

            self.num_rounds += 1

            # Pause for 1 second
            self.visualizer.wait(1)

        # The following line waits until the user closes the Pygame window
        self.visualizer.wait_for_exit()

        return self._calculate_stats()

    def handle_disembarking(self) -> None:
        """Handle people leaving elevators.

        Hints:
        - You shouldn't loop over a list (e.g. elevator.passengers) and mutate it within the
          loop body. This will cause unexpected behaviour due to how Python implements looping!
        - It's fine to reassign elevator.passengers to a new list. If you do so,
          make sure to call elevator.update() so that the new "fullness" of the elevator
          gets visualized properly.
        """
        for elevator in self.elevators:
            # Correctly referencing the `current_floor` attribute
            current_floor = elevator.current_floor
            disembarking_passengers = []

            # Identify passengers who need to disembark
            for passenger in elevator.passengers:
                if passenger.target == current_floor:
                    disembarking_passengers.append(passenger)

            # Visualize disembarking and update the elevator's passengers list
            for passenger in disembarking_passengers:
                self.visualizer.show_disembarking(passenger, elevator)
                elevator.passengers.remove(passenger)

            # Reflect the new state of the elevator after some passengers have disembarked
            elevator.update()

            self.completed_people.extend(disembarking_passengers)

    def generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        # Generate new arrivals for this round using the arrival_generator
        new_arrivals = self.arrival_generator.generate(round_num)

        # Update the waiting dictionary with the new arrivals
        for floor_num, new_people in new_arrivals.items():
            self.waiting[floor_num].extend(new_people)

        # Visualize the new arrivals using the visualizer
        self.visualizer.show_arrivals(new_arrivals)

        # Update the total_arrivals attribute
        for new_people in new_arrivals.values():
            self.total_arrivals += len(new_people)

    def handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        # Loop through each elevator in the simulation
        for floor_num, people in self.waiting.items():
            for elevator in self.elevators:
                # Check if the elevator is at this floor
                if elevator.current_floor == floor_num:
                    # While there's room in the elevator and people waiting on this floor
                    while len(elevator.passengers) < elevator.capacity and people:
                        person = people.pop(0)  # Remove the first person from the waiting list
                        elevator.passengers.append(
                            person)  # Add the person to the elevator's passengers
                        self.visualizer.show_boarding(person, elevator)
                        elevator.update()

    def move_elevators(self) -> None:
        """Update elevator target floors and then move them."""
        # 1. Call the moving algorithm’s update_target_floors method to update elevator
        # target floors.
        self.moving_algorithm.update_target_floors(self.elevators, self.waiting, self.num_floors)

        # 2. Move each elevator one floor closer to its target floor and
        # 3. For each elevator, calculate the direction it moved in
        directions = []  # List to store the direction of each elevator

        for elevator in self.elevators:
            # If the elevator's current floor is less than its target floor, it should go up
            if elevator.current_floor < elevator.target_floor:
                elevator.current_floor += 1
                directions.append(Direction.UP)

            # If the elevator's current floor is greater than its target floor, it should go down
            elif elevator.current_floor > elevator.target_floor:
                elevator.current_floor -= 1
                directions.append(Direction.DOWN)

            # If the elevator's current floor is the same as its target floor, it should stay
            else:
                directions.append(Direction.STAY)

        # Visualize the elevator moves using the visualizer
        self.visualizer.show_elevator_moves(self.elevators, directions)

    def update_wait_times(self) -> None:
        """Update the waiting time for every person waiting in this simulation.

        Note that this includes both people waiting for an elevator AND people
        who are passengers on an elevator. It does not include people who have
        reached their target floor.
        """
        # Update the waiting time for each person waiting at each floor
        for people in self.waiting.values():
            for person in people:
                person.wait_time += 1

        # Update the waiting time for each person inside each elevator
        for elevator in self.elevators:
            for person in elevator.passengers:
                person.wait_time += 1

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> dict[str, int]:
        """Report the statistics for the current run of this simulation.

        Preconditions:
        - This method is only called after the simulation rounds have finished

        You MAY change the interface for this method (e.g., by adding new parameters).
        We won't call it directly in our testing.
        """
        # People who reached their target
        people_completed = len(self.completed_people)

        # Calculate max and average time if there are completed people
        if people_completed > 0:
            max_time = max(person.wait_time for person in self.completed_people)
            avg_time = sum(person.wait_time for person in self.completed_people) // people_completed
        else:
            max_time = -1
            avg_time = -1

        return {
            'num_rounds': self.num_rounds,
            'total_people': self.total_arrivals,
            'people_completed': people_completed,
            'max_time': max_time,
            'avg_time': avg_time
        }


###############################################################################
# Simulation runner
###############################################################################
def run_example_simulation() -> dict[str, int]:
    """Run a sample simulation, and return the simulation statistics.

    This function is provided to help you test your work. You MAY change it
    (e.g., by changing the configuration values) for further testing.
    """
    num_floors = 6
    num_elevators = 2
    elevator_capacity = 2

    config = {
        'num_floors': num_floors,
        'num_elevators': num_elevators,
        'elevator_capacity': elevator_capacity,
        'arrival_generator': a1_algorithms.SingleArrivals(num_floors),
        'moving_algorithm': a1_algorithms.EndToEndLoop(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':
    # We haven't provided any doctests for you, but if you add your own the following
    # code will run them!
    import doctest
    doctest.testmod()

    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    sample_run_stats = run_example_simulation()
    print(sample_run_stats)

    # Uncomment the python_ta lines below and run this module.
    # This is different that just running doctests! To run this file in PyCharm,
    # right-click in the file and select "Run a1_simulation" or "Run File in Python Console".
    #
    # python_ta will check your work and open up your web browser to display
    # its report. For full marks, you must fix all issues reported, so that
    # you see "None!" under both "Code Errors" and "Style and Convention Errors".
    # TIP: To quickly uncomment lines in PyCharm, select the lines below and press
    # "Ctrl + /" or "⌘ + /".
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['a1_entities', 'a1_visualizer', 'a1_algorithms'],
        'max-nested-blocks': 4,
        'max-attributes': 10,
        'max-line-length': 100
    })
