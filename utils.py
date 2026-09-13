try:
    from matplotlib.colors import to_rgb 
    from termcolor import colored
except:
    print("Missing dependencies: try uv sync")
    import sys
    sys.exit(1)

class Colors:
    @staticmethod
    def colorize(string, color):
        try:
            rgb = tuple(map(lambda c: c * 255, to_rgb(color)))
        except:
            rgb = (255, 255, 255)
        return colored(string, rgb)
