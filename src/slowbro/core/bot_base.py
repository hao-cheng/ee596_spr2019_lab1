from typing import Tuple, Dict, Any
from abc import ABC, abstractmethod
import logging

from .user_message import UserMessage
from .bot_message import BotMessage
from .round_saver import (RoundSaverAdapterBase, RoundSaver)
from .slowbro_logger import SlowbroLogger


logger = logging.getLogger(__name__)


class BotBase(ABC):
    """Slowbro Bot base class.
    """

    def __init__(self,
                 round_saver_adapter: RoundSaverAdapterBase) -> None:
        """Constructor."""

        self._round_saver = RoundSaver(
            saver_adapter=round_saver_adapter
        )


    def handle_message(
            self,
            user_message: UserMessage,
            ser_session_attributes: Dict[str, Any]
    ) -> Tuple[BotMessage, Dict[str, Any]]:
        """Handles the incoming user message and returns the bot response.

        Incrementally populates the round_attributes.
        """

        (
            round_index,
            ser_round_attributes,
            bot_message,
            ser_session_attributes
        ) = self._handle_message_impl(user_message,
                                      ser_session_attributes)

        # stores round attributes
        self._save_round_attributes(user_message.session_id,
                                    round_index,
                                    ser_round_attributes)

        return (
            bot_message,
            ser_session_attributes
        )


    @abstractmethod
    def _handle_message_impl(
            self,
            user_message: UserMessage,
            ser_session_attributes: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any], BotMessage, Dict[str, Any]]:
        """Implementation of the message handling logic."""
        pass


    def handle_exception(self,
                         user_message: UserMessage,
                         ser_session_attributes: Dict[str, Any],
                         exception: Exception) -> Tuple[BotMessage,
                                                        Dict[str, Any]]:
        """Handles exception.
        Resets parameters and re-run handle_message.
        """

        slowbro_logger = SlowbroLogger(
            logger=logger,
            request_id=user_message.request_id
        )

        try:
            raise exception
        except Exception: # pylint: disable=W0703
            slowbro_logger.exception(
                'Exception Occurred! Session Attributes: \n%s',
                ser_session_attributes
            )

        # TODO: send email notification

        return self.handle_message(user_message, {})


    def _save_round_attributes(self,
                               session_id: str,
                               round_index: int,
                               ser_round_attributes: Dict[str, Any]):
        """Saves round attributes.
        """

        self._round_saver.save_round(
            session_id=session_id,
            round_index=round_index,
            round_attributes=ser_round_attributes
        )
