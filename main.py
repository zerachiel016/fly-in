"""Main entry point for the Fly-in drone routing simulation.

This module coordinates loading the map configuration file, parsing the
network topology, discovering optimal flight paths via the pathfinder,
and launching the discrete-turn drone simulation.
"""

from map_builder import MapBuilder
from pathfinder import Pathfinder
from sim import Sim

if __name__ == "__main__":
    try:
        map = MapBuilder.map
        MapBuilder.build_map()
        paths = Pathfinder.build_paths(map)
        Sim.start(map, paths)
    except Exception as e:
        print("Unexpected Error:", e)
    except KeyboardInterrupt:
        print("User interrupted program execution")
