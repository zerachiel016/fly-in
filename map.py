from utils import Colors

class Map:
    class Hub:
        get_cost = {
            'priority': 0.9,
            'normal': 1,
            'restricted': 2,
            'blocked': -1,
        }

        def __init__(self, name, x, y, meta={}, start=False, end=False):
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
            self.connections = {}
            self.colorized = Colors.colorize(self.name, self.color)

    def __init__(self) -> None:
        self.nb_drones = None
        self.hubs = {}

    def set_nb_drones(self, v: int):
        if self.hubs:
            raise Exception("nb_drones must be defined in the first line")
        elif self.nb_drones is not None:
            raise Exception("Duplicate nb_drones")
        self.nb_drones = v

    def add_hub(self, dec: list[str], meta):
        start = end = False
        if dec[0] == "start_hub:":
            if any(h.start for h in self.hubs.values()):
                raise Exception(f"Duplicate 'start_hub'")
            if 'zone' in meta and meta['zone'] == 'blocked':
                raise Exception("start_hub can't be a blocked zone")
            start = True
        elif dec[0] == "end_hub:":
            if any(h.end for h in self.hubs.values()):
                raise Exception(f"Duplicate 'end_hub'")
            if 'zone' in meta and meta['zone'] == 'blocked':
                raise Exception("end_hub can't be a blocked zone")
            end = True

        if not all(dec[1] != h.name for h in self.hubs.values()):
            raise Exception(f"Duplicate '{dec[1]}' hub name")

        self.hubs[dec[1]] = Map.Hub(dec[1], int(dec[2]), int(dec[3]), meta, start, end)

    def add_connection(self, hub_name, to_hub_name, max_link_capacity):
        hub1 = self.hubs.get(hub_name)
        hub2 = self.hubs.get(to_hub_name)
        if not hub1 or not hub2:
            raise Exception(f"Invalid connection: '{hub_name}' or '{to_hub_name}' does not exist")
        if (hub1.connections.get(hub2.name)):
            raise Exception(f"Already exisiting connection {hub_name}-{to_hub_name}")
        hub1.connections[hub2.name] = max_link_capacity
        hub2.connections[hub1.name] = max_link_capacity

