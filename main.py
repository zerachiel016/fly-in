from map_builder import MapBuilder
from map import Map
from pathfinder import Pathfinder
from sim import Sim

def main():
    map = MapBuilder.map
    MapBuilder.build_map()
    paths = Pathfinder.build_paths(map)
    Sim.start(map, paths)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Unexpected Error:", e)
    except KeyboardInterrupt:
        print("User interrupted program execution")
