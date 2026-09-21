*This project has been created as part of the 42 curriculum by zdadsi.*

# Fly-in: Autonomous Drone Fleet Routing System

## Description

**Fly-in** is a discrete turn-based simulation system designed to route an autonomous fleet of drones from a designated start base (`start_hub`) to a target destination (`end_hub`) through a network of connected zones in the fewest possible simulation turns.

The simulation navigates a topological graph under strict real-world constraints:
- **Zone Occupancy (`max_drones`)**: Each hub allows a limited number of concurrent drones (default: 1 drone).
- **Link Capacities (`max_link_capacity`)**: Each bidirectional edge permits a restricted number of concurrent drone traversals per turn.
- **Zone Types & Movement Costs**:
  - `normal`: Standard zone requiring 1 simulation turn.
  - `priority`: Preferred zone requiring 1 turn, favored during route selection.
  - `restricted`: High-risk or complex zone requiring 2 turns to traverse.
  - `blocked`: Impassable zone; drones cannot enter or path through it.
- **Simultaneous Movements**: Multiple drones can advance concurrently in a single turn as long as edge and zone capacity constraints are respected.

---

## Instructions

### Prerequisites
- **Python**: `>= 3.10`
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (or standard Python `venv` + `pip`)

### Installation
Synchronize project dependencies using `uv` via the provided Makefile:
```bash
make install
```
*(Alternatively: `uv sync` or `pip install -r pyproject.toml`)*

### Execution
Run the simulation on any valid map file:
```bash
make run map=maps/easy/01_linear_path.txt
```
Or execute directly using the Python interpreter:
```bash
uv run main.py maps/easy/01_linear_path.txt
```

### Debugging
Launch the simulation with Python's built-in interactive debugger (`pdb`):
```bash
make debug
```

### Linting & Static Analysis
Verify code standards and static typing:
```bash
make lint
```
This runs:
- `flake8 .` (adherence to PEP 8 style standards)
- `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`

To run strict type checking:
```bash
uv run mypy . --strict
```

### Cleaning
Clean temporary bytecode and cache directories (`__pycache__`, `.mypy_cache`):
```bash
make clean
```

---

## Resources & AI Usage

### References
- **Dijkstra's Algorithm**: Edsger W. Dijkstra, *A Note on Two Problems in Connexion with Graphs* (1959).
- **Network Flow & Routing**: Concepts of edge capacity constraints, bottleneck mitigation, and disjoint paths in graph theory.
- **Python Documentation**:
  - [`heapq`](https://docs.python.org/3/library/heapq.html) — Priority queue implementation for Dijkstra's algorithm.
  - [`typing`](https://docs.python.org/3/library/typing.html) — Static type hints for robust codebase reliability.
- **Python Standards**:
  - [PEP 257](https://peps.python.org/pep-0257/) — Docstring Conventions.
  - [PEP 8](https://peps.python.org/pep-0008/) — Style Guide for Python Code.

### AI Usage Disclosure
Artificial Intelligence (AI) was utilized throughout the development and maintenance of this project in accordance with Chapter II instructions:
- **Documentation & Docstrings**: Assisted in generating PEP 257 and Google-style docstrings across all modules, classes, and methods, ensuring comprehensive documentation of purpose, arguments, return values, and exceptions.
- **Static Typing & Linter Compliance**: Used to verify edge-case type annotations satisfying `mypy --strict` and `flake8` requirements without altering core simulation mechanics.
- **Specification Audit**: Assisted in reviewing codebase implementation against `SUBJECT.md` requirements (parser constraints, turn mechanics, and benchmark targets).

---

## Algorithm Choices and Implementation Strategy

### 1. Object-Oriented Network Representation
The network is structured using clean object-oriented abstractions:
- **`Map` & `Map.Hub`**: Represents the network topology, tracking spatial coordinates `(x, y)`, zone categories, entry costs, concurrent drone capacities, and adjacency lists.
- **`Drone`**: Tracks individual drone state, including remaining route sequence, current zone, and in-flight transit flags.
- **`Sim`**: Discrete turn controller maintaining simulation turns, capacity states, and formatted output generation.

### 2. Weighted Dijkstra Pathfinding
Shortest routes are discovered using a priority-queue-based Dijkstra algorithm ([`Pathfinder.djikstra`](file:///goinfre/aymel-ha/a/pathfinder.py)):
- **Cost Weights**:
  - `priority`: `0.9` (heavily incentivized over standard routes)
  - `normal`: `1.0`
  - `restricted`: `2.0`
  - `blocked`: Excluded during neighbor traversal
- By assigning `0.9` cost to `priority` zones, Dijkstra naturally selects priority corridors whenever available without distorting overall turn counts.

### 3. Edge-Disjoint Secondary Route Discovery
To avoid congestion on single paths and distribute drone traffic:
- After finding the primary shortest path, the algorithm identifies a **secondary alternate path** ([`Pathfinder.get_second_path`](file:///goinfre/aymel-ha/a/pathfinder.py)) by systematically masking each edge of the primary path and re-running Dijkstra.
- The lowest-cost alternate route is selected as the secondary corridor.
- Drones are distributed across the primary and secondary routes in an alternating pattern (`D1` on main, `D2` on second, etc.), maximizing aggregate network throughput.

### 4. Turn Mechanics & Capacity Enforcement
At each discrete simulation turn:
1. **Capacity Copying**: Connection capacities are renewed for the turn.
2. **Restricted Zone In-Flight Transit**: Drones flying into `restricted` zones spend their first turn occupying the transit link (`D<ID>-<source>-<target>`) with `pending=True`, and complete their arrival into the destination hub on the following turn (`D<ID>-<target>`).
3. **Simultaneous Flow**: Drones move concurrently when `connections[con] > 0` and `occupency[target] > 0`. Advancing drones immediately free up space in their departure zones for trailing drones.

---

## Visual Representation Features

The project includes an integrated ANSI terminal color styling engine ([`utils.py`](file:///goinfre/aymel-ha/a/utils.py)):
- **Zone Coloring**: Hub names in simulation output lines are colorized based on their `[color=<name>]` metadata (e.g. `green`, `blue`, `orange`, `red`).
- **Color Conversion**: Translates named colors and hex strings to true RGB values using `matplotlib.colors` and renders them with `termcolor`. Unspecified colors default to clean white.
- **User Experience Enhancement**:
  - Clearly differentiates hub roles: green for start hubs, red/gold for destinations, custom colors for bottlenecks and routes.
  - Distinguishes drones still in flight toward restricted zones (`D<ID>-zoneA-zoneB`) from landed drones (`D<ID>-zoneB`).

---

## Example Input and Expected Output

### Input Map File (`maps/easy/01_linear_path.txt`)
```text
# Easy Level 1: Linear path
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=orange]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

### Execution Output
```bash
$ uv run main.py maps/easy/01_linear_path.txt
D1-waypoint1 
D1-waypoint2 D2-waypoint1 
D1-goal D2-waypoint2 
D2-goal 
Total turns: 4
```

### Output Interpretation
- **Turn 1**: Drone `D1` departs `start` and enters `waypoint1`. `D2` waits at `start` due to `waypoint1` capacity (`max_drones=1`).
- **Turn 2**: `D1` advances to `waypoint2`, freeing `waypoint1`. `D2` immediately enters `waypoint1`.
- **Turn 3**: `D1` reaches `goal` and is delivered. `D2` advances to `waypoint2`.
- **Turn 4**: `D2` reaches `goal`. All drones delivered in **4 turns** (beating the reference target of `<= 6 turns`).

---

## Benchmark Performance Results

| Map Category | Map Name | Fleet Size | Subject Target | Achieved Turns | Result |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Easy** | `01_linear_path.txt` | 2 drones | $\le$ 6 turns | **4 turns** | Target Beaten |
| **Easy** | `02_simple_fork.txt` | 4 drones | $\le$ 8 turns | **4 turns** | Target Beaten |
| **Easy** | `03_basic_capacity.txt` | 4 drones | $\le$ 6 turns | **6 turns** | Target Met |
| **Medium** | `01_dead_end_trap.txt` | 5 drones | $\le$ 12 turns | **8 turns** | Target Beaten |
| **Medium** | `02_circular_loop.txt` | 6 drones | $\le$ 15 turns | **15 turns** | Target Met |
| **Medium** | `03_priority_puzzle.txt` | 5 drones | $\le$ 12 turns | **8 turns** | Target Beaten |
| **Hard** | `01_maze_nightmare.txt` | 8 drones | $\le$ 30 turns | **13 turns** | Target Beaten |
| **Hard** | `02_capacity_hell.txt` | 12 drones | $\le$ 35 turns | **16 turns** | Target Beaten |
| **Hard** | `03_ultimate_challenge.txt` | 15 drones | $\le$ 45 turns | **27 turns** | Target Beaten |
| **Challenger** | `01_the_impossible_dream.txt` | 25 drones | $\le$ 45 turns | **43 turns** | **Record Beaten** |
