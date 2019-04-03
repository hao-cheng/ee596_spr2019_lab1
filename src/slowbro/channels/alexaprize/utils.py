from typing import Tuple, Dict, List, Any
import logging

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.response_helper import ResponseFactory
from ask_sdk_core.utils import is_request_type
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_model.ui import SimpleCard
from slowbro.core.user_message import (UserMessage,
                                       AsrHypothesisToken,
                                       AsrHypothesisUtterance)
from slowbro.core.bot_message import BotMessage


logger = logging.getLogger(__name__)


def parse_handler_input(
        handler_input: HandlerInput,
) -> Tuple[UserMessage, Dict[str, Any]]:
    """Parses the ASK-SDK HandlerInput into Slowbro UserMessage.

    Returns the UserMessage object and serialized SessionAttributes.
    """

    request_envelope = handler_input.request_envelope

    text: str
    asr_hypos: List[AsrHypothesisUtterance] = []
    if is_request_type("LaunchRequest")(handler_input):
        # This is a launch request.
        text = ''
    elif is_request_type("IntentRequest")(handler_input):
        slots = request_envelope.request.intent.slots
        slot_text = slots.get('Text', None)
        if slot_text is not None:
            text = slot_text.value
        else:
            text = ''

        if hasattr(request_envelope.request, 'speechRecognition'):
            hypotheses = request_envelope.request.speechRecognition.get('hypotheses', [])
            asr_hypos.extend([
                AsrHypothesisUtterance(
                    [
                        AsrHypothesisToken(
                            token['value'],
                            token['confidence'],
                            token['startOffsetInMilliseconds'],
                            token['endOffsetInMilliseconds']
                        )
                        for token in hypo['tokens']
                    ],
                    hypo['confidence']
                )
                for hypo in hypotheses
            ])
        elif text:
            # NOTE: create a fake ASR hypo using the text field.
            asr_hypos.extend([
                AsrHypothesisUtterance(
                    [
                        AsrHypothesisToken(
                            token,
                            -1,
                            -1,
                            -1
                        )
                        for token in text.split(' ')
                    ],
                    -1
                )
            ])

        if not text:
            # Try to recover the text using asr_hypos.
            # Otherwise, raise an exception.
            if asr_hypos:
                text = asr_hypos[0].__str__()
            else:
                raise Exception('Unable to find "text" from handler input:',
                                handler_input)
    else:
        raise Exception('Unable to parse handler input:',
                        handler_input)


    serializer = DefaultSerializer()
    user_message = UserMessage(
        payload=serializer.serialize(request_envelope),
        channel='alexaprize',
        request_id=request_envelope.request.request_id,
        session_id=request_envelope.session.session_id,
        user_id=request_envelope.session.user.user_id,
        text=text,
        asr_hypos=asr_hypos
    )

    attributes_manager = handler_input.attributes_manager
    ser_session_attributes = attributes_manager.session_attributes

    return (user_message, ser_session_attributes)


def build_response(bot_message: BotMessage,
                   response_builder: ResponseFactory) -> None:
    """Builds a response.
    """

    if bot_message.response_ssml is not None:
        response_builder.speak(
            bot_message.response_ssml
        )

    if (bot_message.card_title is not None
            or bot_message.card_content is not None):
        response_builder.set_card(
            SimpleCard(
                bot_message.card_title,
                bot_message.card_content
            )
        )

    if bot_message.reprompt_ssml is not None:
        response_builder.ask(
            bot_message.reprompt_ssml
        )

    response_builder.set_should_end_session(
        bot_message.should_end_session
    )
