import sys
from map import Map

class MapBuilder:
    map = Map()

    @staticmethod
    def _find_map_file_path() -> str:
        if len(sys.argv) != 2:
            print("Invalid number of arguments")
            print("Usage python main.py <map_file>")
        else:
            try:
                with open(sys.argv[1], "r") as file:
                    return file.read()
            except OSError as e:
                print(f"Error: Invalid map file ({e})")
        sys.exit(1)

    @staticmethod
    def parse_map() -> list[list[str]]:
        content = MapBuilder._find_map_file_path()

        parsed = []
        for i, l in enumerate(content.split("\n")):
            l = [w for w in l.split("#", 1)[0].strip().split(" ") if w] or ['']
            parsed += [l]
        return parsed

    @staticmethod
    def handle_nbdrones(dec: list[str]):
        if len(dec) != 2:
            raise Exception("Invalid nb_drones params")
        try:
            val = int(dec[1])
        except:
            raise Exception("Invalid nb_drones value type")
        if val < 1:
            raise Exception("Invalid drone number")
        MapBuilder.map.set_nb_drones(val)

    @staticmethod
    def parse_meta(meta, allowed):
        if not (meta[0] == '[' and meta[-1] == ']'):
            raise Exception(f"Missing brackets: ... {meta} ...")
        m = ""
        try:
            meta = meta[1:-1].strip()
            if not meta:
                return meta
            meta = meta.split(" ")
            _dict = {}
            for m in meta:
                key, value = m.split("=", 1)
                if not allowed[key](value):
                    raise
                elif key in _dict:
                    m = f"Duplicate '{key}'"
                    raise
                _dict[key] = value
        except:
            raise Exception(f"Invalid Metadata: {m}")
        return _dict

    allowed_hub_meta = {
        "zone": lambda v: v.lower() in {"normal", "blocked", "restricted", "priority"},
        "color": lambda v: v.isalpha(),
        "max_drones": lambda v: int(v) > 0,
    }

    @staticmethod
    def handle_hub(dec: list[str]):
        meta = {}
        if len(dec) < 4:
            raise Exception("Invalid hub parameters")
        elif len(dec) > 4:
            meta = MapBuilder.parse_meta(" ".join(dec[4:]), MapBuilder.allowed_hub_meta)
            dec = dec[:4]

        try:
            int(dec[2])
            int(dec[3])
        except:
            raise Exception(f"Invalid coordinates value: (x:{dec[2]}, y:{dec[3]})")

        MapBuilder.map.add_hub(dec, meta)

    allowed_connection_meta = { "max_link_capacity": lambda v: int(v) > 0 }

    @staticmethod
    def handle_connection(dec: list[str]):
        max_link_capacity = 1
        if len(dec) < 2:
            raise Exception("Invalid connection parameters")
        elif len(dec) > 2:
            meta = MapBuilder.parse_meta(" ".join(dec[2:]), MapBuilder.allowed_connection_meta)
            max_link_capacity = int(meta['max_link_capacity'])

        if dec[1].count("-") != 1:
            raise Exception(f"Invalid connection: {dec[1]}")

        hub1, hub2 = dec[1].split("-", 1)
        MapBuilder.map.add_connection(hub1, hub2, max_link_capacity)

    handlers = {
        "nb_drones:": handle_nbdrones,
        "start_hub:": handle_hub,
        "hub:": handle_hub,
        "end_hub:": handle_hub,
        "connection:": handle_connection,
    }

    @staticmethod
    def build_map():
        map_content = MapBuilder.parse_map()
        for i, declaration in enumerate(map_content, start=1):
            dec_type = declaration[0]
            if not dec_type or dec_type[0] == "#":
                continue
            try:
                def handle_other(_):
                    raise Exception(f"'{dec_type}' is not allowed")
                MapBuilder.handlers.get(dec_type, handle_other)(declaration)
            except Exception as e:
                print(f"[Line {i}] MapError:", e)
                sys.exit(1)
        if not any(h.start for h in MapBuilder.map.hubs.values()):
            print("MapError: Undefined start_hub")
        elif not any(h.end for h in MapBuilder.map.hubs.values()):
            print("MapError: Undefined end_hub")
        elif not MapBuilder.map.nb_drones:
            print("MapError: Undefined nb_drones")
        else:
            return
        sys.exit(1)

