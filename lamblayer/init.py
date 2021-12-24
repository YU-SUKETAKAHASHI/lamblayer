import os
import json
import requests

import click

from .lamblayer import Lamblayer


class Init(Lamblayer):
    def __init__(self, profile, region, log_level):
        super().__init__(profile, region, log_level)

    def __call__(self, function_name, download):
        self.init(function_name, download)

    def init(self, function_name, download):
        """
        Inisialize function config file, and download layer zip contents.

        Params
        ======
        function_name: str
            the name of function for inisialize
        download: bool
            download all layer zip contents, or not.

        """
        self.logger.info(f"starting init {function_name}")
        response = self.session.client("lambda").get_function(
            FunctionName=function_name
        )
        try:
            layers = response["Configuration"]["Layers"]
            layer_version_arns = [layer["Arn"] for layer in layers]
        except KeyError:
            layer_version_arns = []

        self.logger.info("createing function.json")
        self.logger.debug(f"function_name: {function_name}")
        self.logger.debug(f"layers: {layer_version_arns}")

        self._gen_function_json(function_name, layer_version_arns)

        if download:
            self.logger.info("starging download layers")

            for layer_version_arn in layer_version_arns:
                self.logger.info(f"downloading {layer_version_arn}")
                layer_content_url = self._get_layer_url(layer_version_arn)
                self._download_layer(layer_content_url)

    def _gen_function_json(self, function_name, layer_version_arns):
        """
        Generate a function config file.

        Params
        ======
        function_name: str
            the name of the function
        layer_version_arns: str
            the ARN of the layer version

        """
        FUNCTION = "function.json"

        config = {
            "FunctionName": function_name,
            "Layers": layer_version_arns,
        }

        if os.path.exists(FUNCTION):
            if not click.confirm(f"Overwrite existing file {FUNCTION}?"):
                self.logger.info("chanceled")
                return 0

        with open(FUNCTION, "w") as f:
            json.dump(config, f, indent=4)

    def _get_layer_url(self, layer_version_arn):
        """
        Return a layer zip content url.

        Params
        ======
        layer_version_arn: str
            the ARN of the layer version

        Returns
        =======
        content_url: str
            a url of layer zip content
        """
        version = int(layer_version_arn.split(":")[-1])
        layer_arn = layer_version_arn.rsplit(":", 1)[0]
        response = self.session.client("lambda").get_layer_version(
            LayerName=layer_arn,
            VersionNumber=version,
        )
        content_url = response["Content"]["Location"]
        return content_url

    def _download_layer(self, layer_content_url):
        """
        Download layer zip contents.
        save path format : ./{layer name}-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.zip

        Params
        ======
        layer_content_url: str
            a url of layer zip content

        """
        save_path = layer_content_url.split("/")[-1].split("?")[0] + ".zip"

        response = requests.get(layer_content_url)

        with open(save_path, "wb") as f:
            f.write(response.content)
