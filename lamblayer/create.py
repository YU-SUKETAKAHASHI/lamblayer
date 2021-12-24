import os
import sys
import time
import json
import shutil
import hashlib

from .lamblayer import Lamblayer
from .exceptions import (
    LamblayerInvalidOptionError,
    LamblayerParamValidationError,
)


class Create(Lamblayer):
    def __init__(self, profile, region, log_level):
        super().__init__(profile, region, log_level)

    def __call__(self, packages, src, wrap_dir1, wrap_dir2, layer_path):
        self.create(packages, src, wrap_dir1, wrap_dir2, layer_path)

    def create(self, packages, src, wrap_dir1, wrap_dir2, layer_path):
        """
        Creates the layer.

        Params
        ======
        packages: str
            packages file path
        src: str
            layer zip archive or src dir path
        wrap_dir1: str
            a wrap directory1 name
        wrap_dir2: str
            a wrap directory2 name
        layer_path: str
            create layer config file path

        """
        self.logger.debug(f"packages: {packages}")
        self.logger.debug(f"src: {src}")
        self.logger.debug(f"layer: {layer_path}")

        if packages and src:
            raise LamblayerInvalidOptionError(
                "`--packages` and `--src` cannot be specified at the same time."
            )
        elif not packages and not src:
            raise LamblayerInvalidOptionError(
                "either `--packages` or `--src` must be specified."
            )

        (
            layer_name,
            description,
            compatible_runtimes,
            license_info,
        ) = self._parse_create_layer_json(layer_path)

        self.logger.info(f"starting create layer {layer_name}")
        self.logger.debug(f"layer_name: {layer_name}")
        self.logger.debug(f"description: {description}")
        self.logger.debug(f"compatible_runtimes: {compatible_runtimes}")
        self.logger.debug(f"license_info: {license_info}")

        if src:
            self.logger.info(f"creating zip archive from {src}")

            # create zip archive
            zipfile = self._create_ziparchive(src, wrap_dir1, wrap_dir2)

            self.logger.info("creating layer")

            # create layer
            response = self.session.client("lambda").publish_layer_version(
                LayerName=layer_name,
                Description=description,
                Content={
                    "ZipFile": zipfile,
                },
                CompatibleRuntimes=compatible_runtimes,
                LicenseInfo=license_info,
            )
            layer_version_arn = response["LayerVersionArn"]
            self.logger.info(f"created {layer_version_arn}")

        if packages:
            self.logger.info("This option is currently not available. Coming soon!!")

    def _create_ziparchive(self, src, wrap_dir1="", wrap_dir2=""):
        """
        Creates a zip archive.
        In layer, folder structure will be following, `{wrap_dir1}/{wrap_dir2}/your_files`.

        Params
        ======
        src: str
            a root directory to put in the layer.
        wrap_dir1: str
            a wrap directory1 name.
        wrap_dir2: str
            a wrap directory2 name.

        Returns
        =======
        zipfile: byte
            Bytes of the zip file

        """
        # generate a temp dir path from timestamp hash.
        timestamp = str(time.time())
        timestamp_hash = hashlib.md5(timestamp.encode()).hexdigest()
        temp_dir = timestamp_hash
        # copy src
        temp_layer_dir = os.path.join(temp_dir, "rawlayer")
        copy_src_dir = os.path.join(temp_dir, "rawlayer", wrap_dir1, wrap_dir2)
        shutil.copytree(src, copy_src_dir)
        # make zip file, and read it into variable.
        base_name = os.path.join(temp_dir, "ziplayer")
        shutil.make_archive(base_name, "zip", root_dir=temp_layer_dir)
        output_path = base_name + ".zip"
        with open(output_path, "rb") as f:
            zipfile = f.read()
        # clean up.
        shutil.rmtree(temp_dir)

        self.logger.info(f"zip archive wrote {sys.getsizeof(zipfile)} bytes")

        return zipfile

    def _parse_packages_json(self, packages_path):
        """
        Parses a packages config file.

        Params
        ======
        packages_path: str
            packages config file path

        Returns
        =======
        arch: str
        runtime: str
        packages: list
        no_deps: int
        """
        with open(packages_path, "r") as f:
            packages_config = json.load(f)
        arch = packages_config.get("Arch")
        runtime = packages_config.get("Runtime")
        packages = packages_config.get("Packages")
        no_deps = packages_config.get("No_deps", 0)

        if not isinstance(arch, str):
            raise LamblayerParamValidationError("Arch", arch, str)
        if not isinstance(runtime, str):
            raise LamblayerParamValidationError("Runtime", runtime, str)
        if not isinstance(packages, (str, list)):
            raise LamblayerParamValidationError("Packages", packages, (str, list))
        if not isinstance(no_deps, int):
            raise LamblayerParamValidationError("No_deps", no_deps, int)

        if isinstance(packages, list):
            packages = "&".join(packages)

        return arch, runtime, packages, no_deps

    def _parse_create_layer_json(self, layer_path):
        """
        Parses a create layer config file.

        Params
        ======
        layer_path: str
            layer config file path

        Returns
        =======
        layer_name: str
        description: str
        compatible_runtimes: list
        license_info: str
        """
        with open(layer_path, "r") as f:
            layer_param = json.load(f)
        layer_name = layer_param.get("LayerName")
        description = layer_param.get("Description")
        compatible_runtimes = layer_param.get("CompatibleRuntimes")
        license_info = layer_param.get("LicenseInfo")

        return layer_name, description, compatible_runtimes, license_info
