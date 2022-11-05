"""
Abstract interface for a CLI application containing a function
to run a unique program, a function to generate a CLI parser,
and a function to run the program from the CLI.
"""

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Optional

from app.core.config import get_settings

settings = get_settings()


class CLIApp(ABC):
    """
    Abstract interface for a CLI application containing a function
    to run a unique program, a function to generate a CLI parser,
    and a function to run the program from the CLI.
    """

    APP_NAME: Optional[str] = None

    @abstractmethod
    def run(self, args, loop) -> None:
        """
        Run the program with the given arguments.
        """
        pass

    @abstractmethod
    def generate_cli(self, subparsers) -> ArgumentParser:
        """
        Generate a CLI parser for the program.
        """
        pass

    def run_from_cli(self, subparsers, args, loop) -> None:
        """
        Run the program from the CLI.
        """
        parser = self.generate_cli(subparsers)
        if parser.prog.split(" ")[1] == self.APP_NAME:
            self.run(args, loop)
