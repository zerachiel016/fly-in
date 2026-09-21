"""Pathfinding algorithm implementation for drone routing.

This module utilizes Dijkstra's algorithm with zone traversal costs to find
optimal paths and edge-disjoint or low-conflict alternative secondary routes
from start_hub to end_hub.
"""

import heapq
import sys
from typing import Any


class Pathfinder:
    """Pathfinding engine for computing optimal drone flight routes."""

    @staticmethod
    def get_path_from_table(
        table: dict[str, tuple[float, str | None]], end: str
    ) -> list[str]:
        """Reconstruct the sequence of hubs from start to end from table.

        Backtracks predecessor pointers from the destination hub to the
        origin, reversing the sequence to produce the forward route.

        Args:
            table (dict[str, tuple[float, str | None]]): Predecessor table
                mapping hub names to (cumulative_cost, predecessor_name).
            end (str): Name of the destination hub.

        Returns:
            list[str]: Ordered list of hub names from start to end.

        Raises:
            None.
        """
        path = []
        cur: str | None = end

        while cur is not None:
            path.append(cur)
            cur = table[cur][1]

        path.reverse()

        return path

    @staticmethod
    def djikstra(
        hubs: dict[str, Any], blocked_con: set[str] | None
    ) -> tuple[list[str], float]:
        """Find the shortest weighted path using Dijkstra's algorithm.

        Considers zone costs (priority=0.9, normal=1, restricted=2),
        bypasses 'blocked' zones, and avoids any specified connection edge.

        Args:
            hubs (dict[str, Any]): Mapping of hub names to Hub instances.
            blocked_con (set[str] | None): A set of two hub names representing
                a connection edge to exclude from search, or None.

        Returns:
            tuple[list[str], float]: A tuple containing the list of hub names
                forming the shortest path and the total path cost. Returns
                ([], 0) if no path exists.

        Raises:
            None.
        """
        table: dict[str, tuple[float, str | None]] = {
            h.name: (0 if h.start else float("inf"), None)
            for h in hubs.values()
        }
        queue: list[tuple[float, str | None]] = [
            (0, next(h.name for h in hubs.values() if h.start))
        ]

        while queue:
            cur_cost, cur_zone = heapq.heappop(queue)
            if cur_zone and hubs[cur_zone].end:
                return (
                    Pathfinder.get_path_from_table(table, cur_zone),
                    table[cur_zone][0],
                )
            if cur_zone is None:
                continue
            for con in hubs[cur_zone].connections:
                new_con_cost = cur_cost + hubs[con].cost
                if (
                    new_con_cost < table[con][0]
                    and hubs[con].zone != "blocked"
                    and {con, cur_zone} != blocked_con
                ):
                    table[con] = (new_con_cost, cur_zone)
                    heapq.heappush(queue, (new_con_cost, con))

        return ([], 0)

    @staticmethod
    def get_second_path(
        main_path: list[str], hubs: dict[str, Any]
    ) -> list[str]:
        """Compute an alternative secondary path by blocking main path edges.

        Iteratively blocks each connection edge along the primary route,
        computes alternate routes via Dijkstra's algorithm, and selects the
        route with the lowest cost.

        Args:
            main_path (list[str]): Hub sequence of the primary path.
            hubs (dict[str, Any]): Mapping of hub names to Hub instances.

        Returns:
            list[str]: Hub sequence of the optimal secondary path, or an empty
                list if no alternative path is available.

        Raises:
            None.
        """
        paths: list[tuple[float, list[str]]] = []

        for blocked_con in (
            set(t) for t in list(zip(main_path, main_path[1:]))
        ):
            path = Pathfinder.djikstra(hubs, blocked_con)
            if path[0]:
                paths += [(path[1], path[0])]

        paths.sort()

        if not paths:
            return []

        return paths[0][1]

    @staticmethod
    def build_paths(map: Any) -> list[list[str]]:
        """Calculate primary and secondary routing paths for the simulation.

        Computes the primary shortest route and attempts to determine a
        secondary alternate route. Terminates program if end hub is
        unreachable.

        Args:
            map (Any): Map instance containing defined hubs and connections.

        Returns:
            list[list[str]]: List containing [main_path, second_path].

        Raises:
            SystemExit: If no path connects the start hub to the end hub.
        """
        main_path = Pathfinder.djikstra(map.hubs, None)[0]

        if not main_path:
            print("PathError: end_hub is not reachable")
            sys.exit(1)

        second_path = Pathfinder.get_second_path(main_path, map.hubs)

        return [main_path, second_path]
