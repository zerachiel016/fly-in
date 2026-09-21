"""Map and hub data structures for the drone routing network.

This module models the simulation environment, representing zones as hubs
with spatial coordinates, capacities, costs, and metadata, alongside
bidirectional connections with link capacity constraints.
"""

from typing import Any

from utils import Colors


class Map:
    """Represents the complete simulation map network.

    Manages the fleet drone count, the registry of all hubs (zones),
    and validates topology constraints including unique start and end hubs.

    Attributes:
        nb_drones (int | None): Total number of drones to route in simulation.
        hubs (dict[str, Map.Hub]): Mapping of hub names to Hub instances.
    """

    class Hub:
        """Represents an individual zone (hub) within the network graph.

        Stores spatial coordinates, occupancy capacity, movement cost,
        visual display color, role flags (start/end), and adjacent hub
        connections.

        Attributes:
            get_cost (dict[str, float]): Lookup table mapping zone types
                ('priority', 'normal', 'restricted', 'blocked') to cost.
            name (str): Unique identifier of the hub.
            x (int): Horizontal coordinate on the map.
            y (int): Vertical coordinate on the map.
            zone (str): Zone category ('normal', 'priority', 'restricted',
                'blocked').
            max_drones (int): Maximum concurrent drone occupancy allowed.
            color (str): Display color for terminal output.
            cost (float): Movement cost in turns to enter this zone.
            start (bool): Flag indicating if this is the start hub.
            end (bool): Flag indicating if this is the end hub.
            connections (dict[str, int]): Adjacent hub names mapped to their
                maximum link traversal capacities.
            colorized (str): Hub name formatted with ANSI terminal color codes.
        """

        get_cost = {
            'priority': 0.9,
            'normal': 1,
            'restricted': 2,
            'blocked': -1,
        }

        def __init__(
            self,
            name: str,
            x: int,
            y: int,
            meta: dict[str, Any] | None = None,
            start: bool = False,
            end: bool = False,
        ) -> None:
            """Initialize a new Hub zone instance.

            Args:
                name (str): Unique name of the hub (cannot contain dashes).
                x (int): Horizontal coordinate of the hub.
                y (int): Vertical coordinate of the hub.
                meta (dict | None, optional): Metadata attributes dictionary
                    (e.g., 'zone', 'max_drones', 'color'). Defaults to None.
                start (bool, optional): True if this hub is the start hub.
                    Defaults to False.
                end (bool, optional): True if this hub is the end hub.
                    Defaults to False.

            Returns:
                None.

            Raises:
                Exception: If the hub name contains a dash ('-').
            """
            if meta is None:
                meta = {}
            if "-" in name:
                raise Exception("Invalid hub name")
            self.name = name
            self.x = x
            self.y = y
            self.zone = meta.get('zone', 'normal')
            self.max_drones = int(meta.get('max_drones', '1'))
            self.color = meta.get('color', 'white')
            self.cost = self.get_cost[self.zone]
            self.start = start
            self.end = end
            self.connections: dict[str, int] = {}
            self.colorized = Colors.colorize(self.name, self.color)

    def __init__(self) -> None:
        """Initialize an empty Map instance with no drones or hubs.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.nb_drones: int | None = None
        self.hubs: dict[str, Map.Hub] = {}

    def set_nb_drones(self, v: int) -> None:
        """Set the total number of drones for the simulation.

        Args:
            v (int): The number of drones to participate in the simulation.

        Returns:
            None.

        Raises:
            Exception: If hubs are already registered when setting drone count
                (violates first-line requirement).
            Exception: If the drone count has already been defined.
        """
        if self.hubs:
            raise Exception("nb_drones must be defined in the first line")
        elif self.nb_drones is not None:
            raise Exception("Duplicate nb_drones")
        self.nb_drones = v

    def add_hub(self, dec: list[str], meta: dict[str, Any]) -> None:
        """Add and validate a new hub in the map network.

        Parses the declaration type ('start_hub:', 'end_hub:', or 'hub:'),
        validates that start and end hubs are unique and not blocked, ensures
        hub names and coordinate pairs are unique, and instantiates the Hub.

        Args:
            dec (list[str]): Hub declaration tokens from the map file
                (e.g., ['hub:', 'name', 'x', 'y']).
            meta (dict): Dictionary of metadata attributes for the hub.

        Returns:
            None.

        Raises:
            Exception: If a duplicate 'start_hub' or 'end_hub' is declared.
            Exception: If 'start_hub' or 'end_hub' is designated as 'blocked'.
            Exception: If a hub with the same name already exists.
            Exception: If a hub with identical (x, y) coordinates already
                exists.
        """
        start = end = False
        if dec[0] == "start_hub:":
            if any(h.start for h in self.hubs.values()):
                raise Exception("Duplicate 'start_hub'")
            if 'zone' in meta and meta['zone'] == 'blocked':
                raise Exception("start_hub can't be a blocked zone")
            start = True
        elif dec[0] == "end_hub:":
            if any(h.end for h in self.hubs.values()):
                raise Exception("Duplicate 'end_hub'")
            if 'zone' in meta and meta['zone'] == 'blocked':
                raise Exception("end_hub can't be a blocked zone")
            end = True

        if any(dec[1] == h.name for h in self.hubs.values()):
            raise Exception(f"Duplicate '{dec[1]}' hub name")
        elif any(
            int(dec[2]) == h.x and int(dec[3]) == h.y
            for h in self.hubs.values()
        ):
            raise Exception(f"Duplicate '{dec[1]}' cords '{dec[2]}, {dec[3]}'")

        self.hubs[dec[1]] = Map.Hub(
            dec[1], int(dec[2]), int(dec[3]), meta, start, end
        )

    def add_connection(
        self, hub_name: str, to_hub_name: str, max_link_capacity: int
    ) -> None:
        """Create a bidirectional connection between two hubs.

        Args:
            hub_name (str): Name of the first hub.
            to_hub_name (str): Name of the second hub.
            max_link_capacity (int): Maximum number of drones that can
                traverse this connection simultaneously.

        Returns:
            None.

        Raises:
            Exception: If either hub does not exist in the map.
            Exception: If a connection between these two hubs already exists.
        """
        hub1 = self.hubs.get(hub_name)
        hub2 = self.hubs.get(to_hub_name)
        if not hub1 or not hub2:
            raise Exception(
                f"Invalid connection: '{hub_name}' or '{to_hub_name}' "
                "does not exist"
            )
        if hub1.connections.get(hub2.name):
            raise Exception(
                f"Already exisiting connection {hub_name}-{to_hub_name}"
            )
        hub1.connections[hub2.name] = max_link_capacity
        hub2.connections[hub1.name] = max_link_capacity
