# std imports
import argparse

# internal im ports
from macpepdb_web_backend import server
from macpepdb_web_backend.utility.configuration import Configuration


class ComandLineInterface:
    def __init__(self):
        self.__parser = argparse.ArgumentParser(description="Tools to run MaxDecoy web")
        self.__parser.set_defaults(func=lambda args: self.__parser.print_help())
        subparsers = self.__parser.add_subparsers()
        server.add_cli_arguments(subparsers)
        Configuration.add_cli_arguments(subparsers)

    def start(self):
        args = self.__parser.parse_args()
        args.func(args)
