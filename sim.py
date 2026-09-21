from itertools import chain

class Drone:
    def __init__(self, path, id) -> None:
        self.id = id
        self.path = path.copy()
        self.cur_zone = self.path.pop(0)
        self.next_zone = lambda : self.path[0] if self.path else None
        self.prev_con = None
        self.pending = False

class Sim:
    turn = 0

    @staticmethod
    def fly_to_next(drone, connections, occupency):
        con = drone.cur_zone, drone.next_zone()

        connections[con] = connections[con] - 1
        occupency[drone.cur_zone] = occupency[drone.cur_zone] + 1
        occupency[drone.next_zone()] = occupency[drone.next_zone()] - 1
        drone.cur_zone = drone.path.pop(0)

    @staticmethod
    def drone_can_move(drone, connections, occupency):
        return connections[drone.cur_zone, drone.next_zone()] > 0 and occupency[drone.next_zone()] > 0

    @staticmethod
    def deploy_drones(map, drones, paths):
        _connections = {}
        occupency = {hub: map.hubs[hub].max_drones for hub in set(chain.from_iterable(paths))}
        start = next(hub for hub, v in map.hubs.items() if v.start)
        end = next(hub for hub, v in map.hubs.items() if v.end)
        occupency[end] = 10**100

        for con in set([*zip(paths[0], paths[0][1:])] + [*zip(paths[1], paths[1][1:])]):
            band_width = min(map.hubs[con[0]].connections[con[1]], map.hubs[con[1]].max_drones)
            _connections[con] = band_width

        import time
        while True:
            _drones = [drone for drone in drones if drone.cur_zone != end]
            if not _drones:
                break;

            connections = _connections.copy()
            for drone in _drones:
                if drone.pending:
                    drone.pending = False
                    continue
                if Sim.drone_can_move(drone, connections, occupency):
                    if map.hubs[drone.next_zone()].zone == "restricted":
                        drone.pending = True
                    Sim.fly_to_next(drone, connections, occupency)
            Sim.turn = Sim.turn + 1


    @staticmethod
    def start(map, paths):
        main = paths[0]
        second = paths[1] if paths[1] else paths[0]

        drones = [Drone(main if nd < map.nb_drones / 2 else second, "D" + str(nd + 1)) for nd in range(map.nb_drones)]

        Sim.deploy_drones(map, drones, paths)
