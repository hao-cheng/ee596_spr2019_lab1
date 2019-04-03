"""Alexa skill request handlers.
"""

import logging

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type
from ask_sdk_model import Response
from slowbro.core.bot_base import BotBase
from slowbro.core.slowbro_logger import SlowbroLogger

from .utils import parse_handler_input
from .utils import build_response

logger = logging.getLogger(__name__)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for LaunchRequest.
    """

    def __init__(self,
                 bot: BotBase) -> None:
        self._bot = bot
        super().__init__()


    def can_handle(self,
                   handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)


    def handle(self,
               handler_input: HandlerInput) -> Response:

        (
            user_message,
            _
        ) = parse_handler_input(handler_input)

        (
            bot_message,
            ser_session_attributes
        ) = self._bot.handle_message(
            user_message,
            dict()
        )

        build_response(bot_message,
                       handler_input.response_builder)

        attributes_manager = handler_input.attributes_manager
        attributes_manager.session_attributes = ser_session_attributes

        return handler_input.response_builder.response


class IntentRequestHandler(AbstractRequestHandler):
    """Handler for IntentRequest.
    """

    def __init__(self,
                 bot: BotBase) -> None:
        self._bot = bot
        super().__init__()


    def can_handle(self,
                   handler_input: HandlerInput) -> bool:
        return is_request_type("IntentRequest")(handler_input)


    def handle(self,
               handler_input: HandlerInput) -> Response:

        (
            user_message,
            ser_session_attributes
        ) = parse_handler_input(handler_input)

        (
            bot_message,
            ser_session_attributes
        ) = self._bot.handle_message(
            user_message,
            ser_session_attributes
        )

        build_response(bot_message,
                       handler_input.response_builder)

        attributes_manager = handler_input.attributes_manager
        attributes_manager.session_attributes = ser_session_attributes

        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for SessionEndedRequest.

    See:
    https://developer.amazon.com/docs/custom-skills/request-types-reference.html#sessionendedrequest
    """

    def __init__(self,
                 bot: BotBase) -> None:
        self._bot = bot
        super().__init__()


    def can_handle(self,
                   handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)


    def handle(self,
               handler_input: HandlerInput) -> Response:
        """Returns an empty response.

        The skill cannot return a response to SessionEndedRequest.
        """

        slowbro_logger = SlowbroLogger(
            logger=logger,
            request_id=handler_input.request_envelope.request.request_id
        )

        slowbro_logger.info(
            'Session ended with reason: %s',
            handler_input.request_envelope.request.reason
        )

        # TODO: collect warnings for reason=='ERROR'

        # The default response is empty.
        return handler_input.response_builder.response
