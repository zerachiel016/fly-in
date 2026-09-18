from map_builder import MapBuilder
from map import Map
from pathfinder import Pathfinder

def main():
    map = MapBuilder.map
    MapBuilder.build_map()
    paths = Pathfinder.build_paths(map)

if __name__ == "__main__":
    main()
