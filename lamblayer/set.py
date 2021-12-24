import json

from .lamblayer import Lamblayer


class Set(Lamblayer):
    def __init__(self, profile, region, log_level):
        super().__init__(profile, region, log_level)

    def __call__(self, function_path):
        self.set_(function_path)

    def set_(self, function_path):
        """
        Set the layers.

        Params
        ======
        function_path: str
            function config file path

        """
        self.logger.debug(f"function: {function_path}")

        function_name, layers = self._parse_function_json(function_path)

        self.logger.info(f"starting set layers to {function_name}")
        self.logger.debug(f"function: {function_name}")
        self.logger.debug(f"layers: {layers}")

        self.session.client("lambda").update_function_configuration(
            FunctionName=function_name,
            Layers=layers,
        )

    def _parse_function_json(self, function_path):
        """
        Parse a function config file, and returns params.

        Params
        ======
        layer_path: str
            layer config file path

        Returns
        =======
        function_name: str
            the name of function.
        layers: list
            the ARNs (Amazon Resource Name) of the layers.
        """
        with open(function_path, "r") as f:
            layer_param = json.load(f)
        function_name = layer_param.get("FunctionName")
        layers_name = layer_param.get("Layers")

        if isinstance(layers_name, str):
            layers_name = [layers_name]

        # If the name of layer is only passed, completes it to the ARN(Amazon Resourse Name) with the latest version number.
        layers = [
            self._gen_layer_arn(l_name, self._get_layer_latest_version_number(l_name))
            if ":" not in l_name
            else l_name
            for l_name in layers_name
        ]

        # update function.json for lambroll.
        if layers_name is not None:
            with open(function_path, "w") as f:
                layer_param["Layers"] = layers
                json.dump(layer_param, f)

        return function_name, layers

    def _get_layer_latest_version_number(self, layer_name):
        """
        Return the latest version number of the layer.

        Params
        ======
        layer_name: str
            the layer name or ARN of the layer

        Returns
        =======
        latest_version: int
            the latest version number of the layer
        """
        response = self.session.client("lambda").list_layer_versions(
            LayerName=layer_name,
        )
        try:
            version = int(response["LayerVersions"][0]["Version"])
        except IndexError:
            version = 1

        return version

    def _gen_layer_arn(self, layer_name, version):
        """
        Return the ARN of the layer.

        Params
        ======
        layer_name: str
            the name of the layer
        version: str, int
            the version number of the layer

        Returns
        =======
        layer_arn: str
            the ARN of the layer.
        """
        return f"arn:aws:lambda:{self.region}:{self.account_id}:layer:{layer_name}:{version}"
