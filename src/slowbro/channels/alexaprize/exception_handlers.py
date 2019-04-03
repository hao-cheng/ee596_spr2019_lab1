"""Alexa skill exception handlers.
"""

import traceback

from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from slowbro.core.bot_base import BotBase

# from .utils import parse_handler_input
# from .utils import build_response


class DefaultExceptionHandler(AbstractExceptionHandler):
    """Handler for exceptions.
    """

    def __init__(self,
                 bot: BotBase) -> None:
        self._bot = bot
        super().__init__()


    def can_handle(self,
                   handler_input: HandlerInput,
                   exception: Exception) -> bool:
        return True


    def handle(self,
               handler_input: HandlerInput,
               exception: Exception) -> Response:

        traceback.print_exc()

        handler_input.response_builder.speak(
            "Something went wrong"
        ).set_should_end_session(True)

        # (
        #     user_message,
        #     session_attributes
        # ) = parse_handler_input(handler_input,
        #                         self._bot,
        #                         self._serializer)

        # (
        #     nlg_attributes,
        #     session_attributes
        # ) = self._bot.handle_exception(
        #     user_message,
        #     session_attributes,
        #     exception
        # )

        # build_response(nlg_attributes,
        #                handler_input.response_builder)

        # attributes_manager = handler_input.attributes_manager
        # attributes_manager.session_attributes = self._serializer.serialize(
        #     session_attributes
        # )

        return handler_input.response_builder.response
