from sys import argv

from view_tk import TetrisViewTk

try:
    {
        "tk": TetrisViewTk
    }[argv[1].lower()]()
except IndexError:
    TetrisViewTk()
except KeyError:
    print("Unavailable GUI chocie.")
    print("Available choices are:")
    print("tk")
