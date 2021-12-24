import os

from logging import getLogger, StreamHandler, Formatter

import boto3


class Lamblayer:
    def __init__(
        self,
        profile,
        region,
        log_level,
    ):
        self.profile = profile
        self.region = region
        self.log_level = log_level
        if self.log_level is None:
            self.log_level = "INFO"

        self.logger = self._get_logger()
        self.session = self._get_session()
        self.account_id = self._get_account_id()

    def _get_session(self):
        """
        Return a new session object.

        lamblayer will look some locations when searching for credentials.
        The mechanism in which lamblayer looks for credentials is to search through
        a list of possible locations and stop as soon as it finds credentials,
        it's almost the same as boto3.
        The order in which lamblayer searches for credentials is:
        1. Passing profile name as option `--profile`.
        2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN)
        3. Shared credential file (~/.aws/credentials)
        4. AWS config file (~/.aws/config)
        5. Assume Role provider
        6. Boto2 config file (/etc/boto.cfg and ~/.boto)
        7. Instance metadata service on an Amazon EC2 instance that has an IAM role configured.


        Returns
        =======
        session:
            boto3.session.Session object
        """
        # create session.
        if (self.profile is not None) and (self.region is not None):
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
        elif (self.profile is not None) and (self.region is None):
            session = boto3.Session(profile_name=self.profile)
            self.region = os.getenv("AWS_DEFAULT_REGION")
        elif (self.profile is None) and (self.region is not None):
            session = boto3.Session(region_name=self.region)
        elif (self.profile is None) and (self.region is None):
            session = boto3.Session()
            self.region = os.getenv("AWS_DEFAULT_REGION")

        self.logger.debug(f"session: {session}")
        return session

    def _get_account_id(self):
        """
        Return the account id　of current session.

        Returns
        =======
        account_id: str
            the account id of current session
        """
        return self.session.client("sts").get_caller_identity().get("Account")

    def _get_logger(self):
        """
        Return a logger.

        Returns
        =======
        logger
        """
        logger = getLogger(__name__)
        logger.setLevel(self.log_level.upper())
        ch = StreamHandler()
        ch.setLevel(self.log_level.upper())
        formatter = Formatter("%(asctime)s: [%(levelname)s]: %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger
