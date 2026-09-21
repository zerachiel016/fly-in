"""Map parsing and validation module for the drone simulation.

This module reads configuration files describing the drone simulation
environment, tokenizes declarations, validates zone and link metadata,
and populates the Map object according to project specifications.
"""

import sys
from typing import Any

from map import Map


class MapBuilder:
    """Static builder class for constructing and validating a simulation Map.

    Provides file ingestion, lexical tokenization, semantic validation of
    drone counts, hub definitions, connection constraints, and metadata tags.

    Attributes:
        map (Map): Shared Map instance populated during parsing.
        allowed_hub_meta (dict): Mapping of allowed hub metadata keys to
            validation predicates.
        allowed_connection_meta (dict): Mapping of allowed connection metadata
            keys to validation predicates.
        handlers (dict): Dispatch dictionary mapping declaration prefixes to
            handler methods.
    """

    map = Map()

    @staticmethod
    def _find_map_file_path() -> str:
        """Validate command-line arguments and read the map file content.

        Reads the path of the map file from the program arguments and returns
        its text contents. Exits if the arguments are invalid or the file
        cannot be read.

        Args:
            None.

        Returns:
            str: Raw text content read from the map file.

        Raises:
            SystemExit: If the number of CLI arguments is not exactly 2 or if
                the file cannot be opened/read.
        """
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
        """Tokenize the map file content into lines of clean tokens.

        Strips comments starting with '#', trims surrounding whitespace, and
        splits lines into word tokens.

        Args:
            None.

        Returns:
            list[list[str]]: List of token lists, where each sublist represents
                one non-comment declaration line.

        Raises:
            None.
        """
        content = MapBuilder._find_map_file_path()

        parsed = []
        for i, raw_line in enumerate(content.split("\n")):
            line_tokens = [
                w for w in raw_line.split("#", 1)[0].strip().split(" ") if w
            ] or ['']
            parsed += [line_tokens]
        return parsed

    @staticmethod
    def handle_nbdrones(dec: list[str]) -> None:
        """Validate and set the number of drones from a declaration.

        Args:
            dec (list[str]): Tokenized declaration line for drone count
                (e.g., ['nb_drones:', '5']).

        Returns:
            None.

        Raises:
            Exception: If the declaration token count is not 2.
            Exception: If the drone count cannot be parsed as an integer.
            Exception: If the drone count is less than 1.
        """
        if len(dec) != 2:
            raise Exception("Invalid nb_drones params")
        try:
            val = int(dec[1])
        except Exception:
            raise Exception("Invalid nb_drones value type")
        if val < 1:
            raise Exception("Invalid drone number")
        MapBuilder.map.set_nb_drones(val)

    @staticmethod
    def parse_meta(meta: str, allowed: dict[str, Any]) -> dict[str, str]:
        """Parse and validate bracketed metadata attributes.

        Extracts key=value pairs enclosed in brackets, verifying each against
        allowed keys, validation lambdas, and duplicate detection.

        Args:
            meta (str): Raw string containing bracketed metadata
                (e.g., '[zone=restricted color=red]').
            allowed (dict): Dictionary mapping allowed metadata keys to
                validator functions returning booleans.

        Returns:
            dict[str, str]: Dictionary of validated key-value attribute pairs,
                or empty dictionary if brackets contained no attributes.

        Raises:
            Exception: If brackets '[' and ']' are missing or malformed.
            Exception: If a key is unknown, fails validation, or appears
                multiple times.
        """
        if not (meta[0] == '[' and meta[-1] == ']'):
            raise Exception(f"Missing brackets: ... {meta} ...")
        m = ""
        try:
            meta = meta[1:-1].strip()
            if not meta:
                return {}
            tokens = meta.split(" ")
            _dict: dict[str, str] = {}
            for m in tokens:
                key, value = m.split("=", 1)
                if not allowed[key](value):
                    raise ValueError(f"Invalid value for {key}")
                elif key in _dict:
                    m = f"Duplicate '{key}'"
                    raise ValueError(m)
                _dict[key] = value
        except Exception:
            raise Exception(f"Invalid Metadata: {m}")
        return _dict

    allowed_hub_meta = {
        "zone": lambda v: v.lower() in {
            "normal", "blocked", "restricted", "priority"
        },
        "color": lambda v: v.isalpha(),
        "max_drones": lambda v: int(v) > 0,
    }

    @staticmethod
    def handle_hub(dec: list[str]) -> None:
        """Process and register a hub declaration.

        Validates parameter length, parses optional bracketed metadata,
        verifies integer coordinates, and delegates hub creation to Map.

        Args:
            dec (list[str]): Tokenized hub declaration line
                (e.g., ['hub:', 'name', 'x', 'y', '[meta]']).

        Returns:
            None.

        Raises:
            Exception: If fewer than 4 tokens are provided.
            Exception: If coordinates cannot be parsed as integers.
            Exception: If metadata syntax or values are invalid.
        """
        meta: dict[str, str] = {}
        if len(dec) < 4:
            raise Exception("Invalid hub parameters")
        elif len(dec) > 4:
            meta = MapBuilder.parse_meta(
                " ".join(dec[4:]), MapBuilder.allowed_hub_meta
            )
            dec = dec[:4]

        try:
            int(dec[2])
            int(dec[3])
        except Exception:
            raise Exception(
                f"Invalid coordinates value: (x:{dec[2]}, y:{dec[3]})"
            )

        MapBuilder.map.add_hub(dec, meta)

    allowed_connection_meta = {"max_link_capacity": lambda v: int(v) > 0}

    @staticmethod
    def handle_connection(dec: list[str]) -> None:
        """Process and register a bidirectional connection declaration.

        Parses connection endpoints, verifies single-hyphen format, extracts
        optional 'max_link_capacity' metadata, and adds the connection to Map.

        Args:
            dec (list[str]): Tokenized connection declaration line
                (e.g., ['connection:', 'hubA-hubB', '[max_link_capacity=2]']).

        Returns:
            None.

        Raises:
            Exception: If fewer than 2 tokens are provided.
            Exception: If connection token does not contain exactly one hyphen.
            Exception: If metadata is invalid or connection creation fails.
        """
        max_link_capacity = 1
        if len(dec) < 2:
            raise Exception("Invalid connection parameters")
        elif len(dec) > 2:
            meta = MapBuilder.parse_meta(
                " ".join(dec[2:]), MapBuilder.allowed_connection_meta
            )
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
    def build_map() -> None:
        """Parse declarations and build the complete simulation map.

        Iterates through tokenized lines, dispatches to corresponding handler
        methods, and verifies that start_hub, end_hub, and nb_drones are
        properly defined.

        Args:
            None.

        Returns:
            None.

        Raises:
            SystemExit: If an unknown declaration prefix is encountered,
                a parsing error occurs, or essential map elements are missing.
        """
        map_content = MapBuilder.parse_map()
        for i, declaration in enumerate(map_content, start=1):
            dec_type = declaration[0]
            if not dec_type or dec_type[0] == "#":
                continue
            try:
                def handle_other(_: list[str]) -> None:
                    """Handle unsupported declaration types.

                    Args:
                        _: Ignored declaration tokens.

                    Returns:
                        None.

                    Raises:
                        Exception: Always raised to indicate invalid
                            declaration.
                    """
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
