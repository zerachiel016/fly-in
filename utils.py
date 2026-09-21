"""Terminal color formatting utilities for drone simulation display.

This module provides color conversion and ANSI terminal styling helpers,
enabling visual distinction of hubs and drones based on map metadata.
"""

import sys

try:
    from matplotlib.colors import to_rgb
    from termcolor import colored
except (ImportError, KeyboardInterrupt) as e:
    if isinstance(e, KeyboardInterrupt):
        print("User interrupted program amidst import")
        sys.exit(1)
    print("Missing dependencies: try uv sync")
    sys.exit(1)


class Colors:
    """Helper class for applying ANSI color styling to strings."""

    @staticmethod
    def colorize(string: str, color: str) -> str:
        """Apply RGB color styling to a string using ANSI escape codes.

        Converts a named color or hex code to RGB values via matplotlib,
        then formats the text using termcolor. Falls back to white if the
        color string cannot be parsed.

        Args:
            string (str): The text to be styled.
            color (str): The color name (e.g., 'red', 'blue') or hex code.

        Returns:
            str: The colorized string formatted with ANSI terminal codes.

        Raises:
            None.
        """
        try:
            r, g, b = to_rgb(color)
            rgb: tuple[int, int, int] = (
                int(r * 255),
                int(g * 255),
                int(b * 255),
            )
        except Exception:
            rgb = (255, 255, 255)
        return colored(string, rgb)
