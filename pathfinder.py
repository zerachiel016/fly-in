import heapq
import sys

class Pathfinder:
    @staticmethod
    def get_path_from_table(table, end):
        path = []
        cur = end

        while cur is not None:
            path.append(cur)
            cur = table[cur][1]

        path.reverse()

        return path

    @staticmethod
    def djikstra(hubs, blocked_con):
        table: dict[str, tuple[float, str | None]] = {h.name: (0 if h.start else float("inf"), None) for h in hubs.values()}
        queue: list[tuple[float, str | None]] = [(0, next(h.name for h in hubs.values() if h.start))]

        while queue:
            cur_cost, cur_zone = heapq.heappop(queue)
            if hubs[cur_zone].end and cur_zone:
                return (Pathfinder.get_path_from_table(table, cur_zone), table[cur_zone][0])
            for con in hubs[cur_zone].connections:
                new_con_cost = cur_cost + hubs[con].cost
                if new_con_cost < table[con][0] and hubs[con].zone != "blocked" and {con, cur_zone} != blocked_con:
                    table[con] = (new_con_cost, cur_zone)
                    heapq.heappush(queue, (new_con_cost, con));

        return ([], 0)
    
    @staticmethod
    def get_second_path(main_path, hubs):
        paths: list[tuple[float, list[str]]] = []

        for blocked_con in (set(t) for t in list(zip(main_path, main_path[1:]))):
            path = Pathfinder.djikstra(hubs, blocked_con)
            if path[0]:
                paths += [(path[1], path[0])]

        paths.sort()

        if not paths:
            return []

        return paths[0][1]


    @staticmethod
    def build_paths(map):
        main_path = Pathfinder.djikstra(map.hubs, None)[0]

        if not main_path:
            print("PathError: end_hub is not reachable")
            sys.exit(1)

        second_path = Pathfinder.get_second_path(main_path, map.hubs)

        return [main_path, second_path]
