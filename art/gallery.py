
import random

PINK = "\033[38;5;213m"
PURPLE = "\033[38;5;141m"
RED = "\033[38;5;196m"
CYAN = "\033[38;5;51m"
WHITE = "\033[97m"
RESET = "\033[0m"

ARTWORKS = [
    {
        "name": "Pixel Cat",
        "art": r"""
          /\_/\
         ( o.o )
          > ^ <
        """
    },
    {
        "name": "Auri Frame",
        "art": r"""
        .-==========-.
        |   A U R I  |
        '-==========-'
        """
    },
    {
        "name": "Demon Star",
        "art": r"""
          . * . * .
        *   DEMON   *
          . * . * .
        """
    },
    {
        "name": "Auri Portal",
        "art": r"""
           /-----\
          / AURI  \
          \       /
           \-----/
        """
    },
    {
        "name": "Digital Heart",
        "art": r"""
          **   **
         ****** ******
          ***********
            *******
              ***
        """
    }
]

COLORS = [PINK, PURPLE, RED, CYAN, WHITE]


def show_gallery():
    print(PURPLE + "\n--- AURITERM COLOR ART ---" + RESET)

    artwork = random.choice(ARTWORKS)
    color = random.choice(COLORS)

    print(CYAN + "Artwork: " + artwork["name"] + RESET)
    print(color + artwork["art"] + RESET)


def list_artworks():
    print(PURPLE + "\n--- ARTWORK COLLECTION ---" + RESET)

    for index, artwork in enumerate(ARTWORKS, start=1):
        print(CYAN + str(index) + ". " + WHITE + artwork["name"] + RESET)


if __name__ == "__main__":
    list_artworks()
    show_gallery()
