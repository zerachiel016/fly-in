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
    @staticmethod
    def colorize(string, color):
        try:
            rgb = tuple(map(lambda c: c * 255, to_rgb(color)))
        except:
            rgb = (255, 255, 255)
        return colored(string, rgb)
