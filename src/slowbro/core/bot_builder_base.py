from typing import Any, Optional
from abc import ABC, abstractmethod
import logging

from aiohttp import web

logger = logging.getLogger(__name__)


def _configure_logging(loglevel: int,
                       logfile: Optional[str]) -> None:
    # NOTE: using logfile_ to deal with the following mypy error
    # Argument "filename" to "basicConfig" has incompatible type
    # "Optional[str]"; expected "str"
    if logfile:
        logfile_: str = logfile
        logging.basicConfig(filename=logfile_,
                            level=loglevel)
    else:
        logging.basicConfig(level=loglevel)

    logging.captureWarnings(True)


class BotBuilderBase(ABC):
    """The bot builder base (abstract) class.
    """

    __slots__ = ()


    def __init__(self,
                 loglevel: int = logging.INFO,
                 logfile: Optional[str] = None) -> None:
        _configure_logging(loglevel,
                           logfile)


    @property
    def lambda_function(self):
        return self._lambda_function


    def run_server(self,
                   host: str,
                   port: str):
        """Runs a server hosting the bot.
        """

        app = web.Application()
        app.router.add_post('/', self._server_handler)

        try:
            web.run_app(app,
                        host=host,
                        port=port)
        except Exception as e:
            raise e


    @abstractmethod
    async def _lambda_function(self,
                               event: Any,
                               context: Any):
        """The AWS Lambda function handler.
        """
        pass


    @abstractmethod
    async def _server_handler(self,
                              req: web.Request) -> web.Response:
        """The server handler.
        """
        pass
