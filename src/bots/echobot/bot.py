from typing import Dict, Any, Tuple
import os
import logging

from slowbro.core.bot_base import BotBase
from slowbro.core.round_saver import DynamoDbRoundSaverAdapter
from slowbro.core.user_message import UserMessage
from slowbro.core.bot_message import BotMessage

from .session_attributes import SessionAttributes
from .round_attributes import RoundAttributes


logger = logging.getLogger(__file__)


def _initialize_session_attributes() -> SessionAttributes:
    """Initializes the session attributes."""
    session_attributes = SessionAttributes(
        round_index=0
    )
    return session_attributes


def _update_session_attributes(
        round_attributes: RoundAttributes
) -> SessionAttributes:
    """Updates the session attributes.

    Because the session attributes are created from the round attributes, we do
    NOT need to save the session attributes separately to DynamoDB.
    """
    session_attributes = SessionAttributes(
        round_index=round_attributes.round_index
    )

    return session_attributes


class Bot(BotBase):
    """Alice bot implementation.
    """

    def __init__(self,
                 dynamodb_table_name: str,
                 dynamodb_endpoint_url: str) -> None:
        """Constructor."""

        round_saver_adapter = DynamoDbRoundSaverAdapter(
            table_name=dynamodb_table_name,
            endpoint_url=dynamodb_endpoint_url
        )
        super().__init__(
            round_saver_adapter=round_saver_adapter,
        )


    def _handle_message_impl(
            self,
            user_message: UserMessage,
            ser_session_attributes: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any], BotMessage, Dict[str, Any]]:
        """Implementation of the message handling logic.

        Incrementally populates the round_attributes.
        """

        if not ser_session_attributes:
            session_attributes = _initialize_session_attributes()
        else:
            session_attributes = SessionAttributes()
            session_attributes.from_dict(ser_session_attributes)

        # =====================
        # Step 1: Initialization
        # =====================
        if session_attributes.round_index is None:
            raise Exception(
                'undefined round_index in session_attributes'
            )

        # restores the session data
        # if session_attributes.round_index > 0:

        bot_message = BotMessage()
        round_attributes = RoundAttributes(
            # increment the round index
            round_index=session_attributes.round_index + 1,
            user_message=user_message,
            bot_message=bot_message
        )

        # =====================
        # Step 2: Generates the bot response
        # =====================
        if round_attributes.round_index == 1:
            bot_message.response_ssml = 'Hello'
            bot_message.reprompt_ssml = 'This is an echo bot.'
            bot_message.should_end_session = False
        else:
            user_utterance = user_message.get_utterance()
            if user_utterance == 'stop':
                bot_message.should_end_session = True
            else:
                bot_message.response_ssml = user_utterance
                bot_message.reprompt_ssml = 'This is an echo bot.'
                bot_message.should_end_session = False

        # =====================
        # Step 3: Stores round attributes
        # =====================
        ser_round_attributes = round_attributes.to_dict()
        del ser_round_attributes['round_index']

        # =====================
        # Step 6: Finalizes session attributes
        # =====================
        session_attributes = _update_session_attributes(round_attributes)
        ser_session_attributes = session_attributes.to_dict()

        return (
            round_attributes.round_index,
            ser_round_attributes,
            round_attributes.bot_message,
            ser_session_attributes
        )
