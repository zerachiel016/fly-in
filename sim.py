"""Discrete turn-based simulation engine for drone movement.

This module models drone fleet progression through the network graph,
managing simultaneous drone departures, zone occupancy limits, connection
link capacities, restricted zone multi-turn transit, and step-by-step output.
"""

from itertools import chain
from typing import Any


class Drone:
    """Represents an individual drone navigating through the network.

    Maintains route progression, current zone location, and in-flight transit
    state for multi-turn restricted zones.

    Attributes:
        id (str): Unique drone identifier (e.g., 'D1', 'D2').
        path (list[str]): Remaining sequence of hubs to traverse.
        cur_zone (str): Current hub where the drone is situated.
        prev_con (tuple[str, str] | None): Previous connection traversed by
            the drone.
        pending (bool): Flag indicating if the drone is currently spending
            an extra turn traversing into a restricted zone.
    """

    def __init__(self, path: list[str], id: str) -> None:
        """Initialize a Drone instance with an assigned route.

        Args:
            path (list[str]): Complete sequence of hub names along the route.
            id (str): Unique identifier for the drone.

        Returns:
            None.

        Raises:
            None.
        """
        self.id = id
        self.path = path.copy()
        self.cur_zone = self.path.pop(0)
        self.prev_con = None
        self.pending = False

    def next_zone(self) -> str | None:
        """Return the next target hub on the drone's remaining path.

        Args:
            None.

        Returns:
            str | None: The name of the next hub to visit, or None if the
                drone has reached the end of its path.

        Raises:
            None.
        """
        return self.path[0] if self.path else None


class Sim:
    """Simulation controller managing discrete turns and drone movements.

    Enforces movement mechanics, tracks turn counts, updates capacity
    constraints, and prints turn-by-turn simulation logs.

    Attributes:
        turn (int): Total number of simulation turns elapsed.
    """

    turn = 0

    @staticmethod
    def fly_to_next(
        drone: Drone,
        connections: dict[tuple[str, str], int],
        occupency: dict[str, int],
    ) -> None:
        """Advance a drone into its next zone and update capacities.

        Decrements available connection capacity for the turn, increments
        occupancy of the departing zone, decrements occupancy of the target
        zone, and advances the drone to the destination hub.

        Args:
            drone (Drone): The drone executing movement.
            connections (dict): Remaining connection traversal capacities.
            occupency (dict): Available occupancy limits per hub.

        Returns:
            None.

        Raises:
            None.
        """
        target = drone.next_zone()
        if target is None:
            return
        con = (drone.cur_zone, target)

        connections[con] = connections[con] - 1
        occupency[drone.cur_zone] = occupency[drone.cur_zone] + 1
        occupency[target] = occupency[target] - 1
        drone.cur_zone = drone.path.pop(0)

    @staticmethod
    def drone_can_move(
        drone: Drone,
        connections: dict[tuple[str, str], int],
        occupency: dict[str, int],
    ) -> bool:
        """Check if a drone can advance to its next zone this turn.

        Verifies that the traversal connection has remaining capacity and
        the target zone has available occupancy.

        Args:
            drone (Drone): The drone requesting movement.
            connections (dict): Remaining connection traversal capacities.
            occupency (dict): Available occupancy limits per hub.

        Returns:
            bool: True if both connection and destination zone have available
                capacity, False otherwise.

        Raises:
            None.
        """
        target = drone.next_zone()
        if target is None:
            return False
        return (
            connections[drone.cur_zone, target] > 0
            and occupency[target] > 0
        )

    @staticmethod
    def deploy_drones(
        map: Any, drones: list[Drone], paths: list[list[str]]
    ) -> None:
        """Execute turn-based simulation until all drones reach the end.

        Coordinates simultaneous movement of eligible drones each turn,
        respects connection and zone capacities, handles multi-turn transit
        delays for restricted zones, prints step movements, and tracks total
        turns.

        Args:
            map (Any): Map object containing hub definitions and colors.
            drones (list[Drone]): List of all drone instances.
            paths (list[list[str]]): List of computed paths.

        Returns:
            None.

        Raises:
            None.
        """
        _connections: dict[tuple[str, str], int] = {}
        occupency = {
            hub: map.hubs[hub].max_drones
            for hub in set(chain.from_iterable(paths))
        }
        end = next(hub for hub, v in map.hubs.items() if v.end)
        occupency[end] = 10**100

        for con in set(
            [*zip(paths[0], paths[0][1:])] + [*zip(paths[1], paths[1][1:])]
        ):
            band_width = min(
                map.hubs[con[0]].connections[con[1]],
                map.hubs[con[1]].max_drones,
            )
            _connections[con] = band_width

        while True:
            _drones = [drone for drone in drones if drone.cur_zone != end
                       or drone.pending]
            if not _drones:
                break

            connections = _connections.copy()
            for drone in _drones:
                if drone.pending:
                    print(
                        f"{drone.id}-{map.hubs[drone.cur_zone].colorized} ",
                        end="",
                    )
                    drone.pending = False
                    continue
                if Sim.drone_can_move(drone, connections, occupency):
                    target = drone.next_zone()
                    if target and map.hubs[target].zone == "restricted":
                        print(
                            f"{drone.id}-{drone.cur_zone}-{target} ",
                            end="",
                        )
                        drone.pending = True
                    elif target:
                        print(
                            f"{drone.id}-{map.hubs[target].colorized} ",
                            end="",
                        )
                    Sim.fly_to_next(drone, connections, occupency)
            print()
            Sim.turn = Sim.turn + 1
        print("Total turns:", Sim.turn)

    @staticmethod
    def start(map: Any, paths: list[list[str]]) -> None:
        """Initialize the drone fleet and begin the simulation.

        Instantiates drones, assigns them alternating paths (primary and
        secondary), and begins the deployment simulation loop.

        Args:
            map (Any): Map object containing fleet size and network structure.
            paths (list[list[str]]): List of primary and secondary routes.

        Returns:
            None.

        Raises:
            None.
        """
        main = paths[0]
        second = paths[1] if paths[1] else paths[0]

        drones = [
            Drone(main if nd % 2 == 0 else second, "D" + str(nd + 1))
            for nd in range(map.nb_drones)
        ]

        Sim.deploy_drones(map, drones, paths)
