from typing import List, Tuple

from flask import Blueprint, Flask


class Blueprints:
    def __init__(self, app: Flask, register: List[Tuple[List[Blueprint], str]]) -> None:
        self.app = app
        self.register = register

    def register_blueprint(self) -> None:
        """
        Register all blueprints in the register.
        """
        for register in self.register:
            self._register_blueprint(register)

    def _register_blueprint(self, register: Tuple[List[Blueprint], str]) -> None:
        """
        Register a list of blueprints with their prefixes.

        :param register: A list of tuples containing a blueprint and its prefix.
        """
        blueprints, prefix = register
        for blueprint in blueprints:
            self.app.register_blueprint(blueprint, url_prefix=prefix)
