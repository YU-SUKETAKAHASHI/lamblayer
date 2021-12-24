import os
import re
from logging import getLogger, StreamHandler, Formatter

import click
from botocore.exceptions import BotoCoreError, ClientError

from .init import Init
from .create import Create
from .set import Set
from .list import List
from .exceptions import LamblayerBaseError


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")


def get_version():
    init = open(os.path.join(ROOT, "__init__.py")).read()
    return VERSION_RE.search(init).group(1)


VERSION = get_version()
RUNTIMES = [
    "python2.7",
    "python3.6",
    "python3.7",
    "python3.8",
    "python3.9",
]
LAMBLAYER_HELP_MESSAGE = f"""
lamblayer : v{VERSION}

lamblayer is a minimal deployment tool for AWS Lambda Layers.
"""


@click.group(help=LAMBLAYER_HELP_MESSAGE)
@click.pass_context
@click.option(
    "--profile",
    default=None,
    help="AWS credential profile",
    show_default=True,
)
@click.option(
    "--region",
    default=None,
    help="AWS region",
)
@click.option(
    "--log-level",
    default=None,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="log level",
    show_default="INFO",
)
def main(ctx, profile, region, log_level):
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["region"] = region
    ctx.obj["log_level"] = log_level


@main.command(help="show lamblayer's version number.")
def version():
    click.echo(f"lamblayer : v{VERSION}")


@main.command(help="create a layer.")
@click.pass_context
@click.option(
    "--profile",
    default=None,
    help="AWS credential profile",
    show_default=True,
)
@click.option(
    "--region",
    default=None,
    help="AWS region",
)
@click.option(
    "--log-level",
    default=None,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="log level",
    show_default=True,
)
@click.option(
    "--packages",
    is_flag=False,
    flag_value="packages.json",
    help="packages file path",
    show_default="packages.json",
)
@click.option(
    "--src",
    is_flag=False,
    flag_value=".",
    help="a root directory to put in the layer.",
    show_default=".",
)
@click.option(
    "--wrap-dir1",
    default="",
    help="a wrap directory1 name",
    show_default=True,
)
@click.option(
    "--wrap-dir2",
    default="",
    help="a wrap directory2 name",
    show_default=True,
)
@click.option(
    "--layer",
    default="layer.json",
    help="layer config file",
    show_default=True,
)
def create(ctx, profile, region, log_level, packages, src, wrap_dir1, wrap_dir2, layer):
    if profile is None:
        profile = ctx.obj["profile"]
    if region is None:
        region = ctx.obj["region"]
    if log_level is None:
        log_level = ctx.obj["log_level"]

    logger = get_logger(log_level)
    logger.info(f"lamblayer : v{VERSION}")

    try:
        create_command = Create(profile, region, log_level)
        create_command(packages, src, wrap_dir1, wrap_dir2, layer)
    except (BotoCoreError, ClientError) as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except LamblayerBaseError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except FileNotFoundError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    else:
        logger.info("completed")


@main.command(help="set layers to function.")
@click.pass_context
@click.option(
    "--profile",
    default=None,
    help="AWS credential profile",
    show_default=True,
)
@click.option(
    "--region",
    default=None,
    help="AWS region",
)
@click.option(
    "--log-level",
    default=None,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="log level",
    show_default=True,
)
@click.option(
    "--function",
    default="function.json",
    help="function config file",
    show_default=True,
)
def set(ctx, profile, region, log_level, function):
    if profile is None:
        profile = ctx.obj["profile"]
    if region is None:
        region = ctx.obj["region"]
    if log_level is None:
        log_level = ctx.obj["log_level"]

    logger = get_logger(log_level)
    logger.info(f"lamblayer : v{VERSION}")

    try:
        set_command = Set(profile, region, log_level)
        set_command(function)
    except (BotoCoreError, ClientError) as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except LamblayerBaseError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except FileNotFoundError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    else:
        logger.info("completed")


@main.command(help="show list of the layers.")
@click.pass_context
@click.option(
    "--profile",
    default=None,
    help="AWS credential profile",
    show_default=True,
)
@click.option(
    "--region",
    default=None,
    help="AWS region",
)
@click.option(
    "--log-level",
    default=None,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="log level",
    show_default=True,
)
def list(ctx, profile, region, log_level):
    if profile is None:
        profile = ctx.obj["profile"]
    if region is None:
        region = ctx.obj["region"]
    if log_level is None:
        log_level = ctx.obj["log_level"]

    logger = get_logger(log_level)
    logger.info(f"lamblayer : v{VERSION}")

    try:
        list_command = List(profile, region, log_level)
        list_command()
    except (BotoCoreError, ClientError) as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except LamblayerBaseError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except FileNotFoundError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    else:
        logger.info("completed")


@main.command(help="initialize function.json")
@click.pass_context
@click.option(
    "--profile",
    default=None,
    help="AWS credential profile",
    show_default=True,
)
@click.option(
    "--region",
    default=None,
    help="AWS region",
)
@click.option(
    "--log-level",
    default=None,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="log level",
    show_default=True,
)
@click.option(
    "--function-name",
    default="LAMBLAYER",
    help="function name for initialize",
    show_default=True,
)
@click.option(
    "--download",
    is_flag=True,
    default=False,
    help="download all layers.zip, or not",
    show_default=True,
)
def init(ctx, profile, region, log_level, function_name, download):
    if profile is None:
        profile = ctx.obj["profile"]
    if region is None:
        region = ctx.obj["region"]
    if log_level is None:
        log_level = ctx.obj["log_level"]

    logger = get_logger(log_level)
    logger.info(f"lamblayer : v{VERSION}")

    try:
        init_command = Init(profile, region, log_level)
        init_command(function_name, download)
    except (BotoCoreError, ClientError) as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except LamblayerBaseError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    except FileNotFoundError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
    else:
        logger.info("completed")


def get_logger(log_level):
    if log_level is None:
        log_level = "INFO"
    logger = getLogger(__name__)
    logger.setLevel(log_level.upper())
    ch = StreamHandler()
    ch.setLevel(log_level.upper())
    formatter = Formatter("%(asctime)s: [%(levelname)s]: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
