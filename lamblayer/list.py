import json

import click

from .lamblayer import Lamblayer


class List(Lamblayer):
    def __init__(self, profile, region, log_level):
        super().__init__(profile, region, log_level)

    def __call__(self):
        self.list_()

    def list_(self):
        """
        Show list of the layers.
        """
        self.logger.info("starting list layers")
        response = self.session.client("lambda").list_layers()
        layers = response["Layers"]

        for layer in layers:
            click.echo(json.dumps(layer, indent=2))
