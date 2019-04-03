from typing import Dict, Any
import json
import datetime
import xml.sax.saxutils
import re

from ask_sdk_model import (RequestEnvelope,
                           Application,
                           Session,
                           Context,
                           Request,
                           User,
                           Permissions,
                           Device,
                           SupportedInterfaces,
                           LaunchRequest,
                           IntentRequest,
                           Intent,
                           Slot,
                           IntentConfirmationStatus,
                           SlotConfirmationStatus,
                           # Response,
                           ResponseEnvelope)
from ask_sdk_model.interfaces.system.system_state import SystemState
from ask_sdk_model.interfaces.audioplayer.audio_player_interface import AudioPlayerInterface
from ask_sdk_model.slu.entityresolution.resolutions import Resolutions
from ask_sdk_model.slu.entityresolution.resolution import Resolution
from ask_sdk_model.slu.entityresolution.status import Status
from ask_sdk_model.slu.entityresolution.status_code import StatusCode
from ask_sdk_core.serialize import DefaultSerializer
from lxml import etree

import requests



SESSION_ID = "amzn1.echo-api.session.0000"
USER_ID = "amzn1.ask.account.0000"
DEVICE_ID = "amzn1.ask.device.0000"
APPLICATION_ID = "amzn1.ask.skill.6f9a57d5-4e2b-452c-9fd3-037240133075"
API_ENDPOINT = "https://api.amazonalexa.com"
REQUEST_ID_BASE = "amzn1.echo-api.request.0000"
RESOLUTION_AUTHORITY_BASE = "amzn1.er-authority.echo-sdk.amzn1.ask.skill.0000"


def create_request_envelope(session_attributes: Dict[str, Any],
                            request: Request) -> RequestEnvelope:
    """Creates a request envelope."""
    application = Application(
        application_id=APPLICATION_ID
    )
    user = User(
        user_id=USER_ID,
        access_token=None,
        permissions=Permissions(
            consent_token=None
        )
    )
    request_envelope = RequestEnvelope(
        version="1.0",
        session=Session(
            new=False,
            session_id=SESSION_ID,
            user=user,
            attributes=session_attributes,
            application=application
        ),
        context=Context(
            system=SystemState(
                application=application,
                user=user,
                device=Device(
                    device_id=DEVICE_ID,
                    supported_interfaces=SupportedInterfaces(
                        audio_player=AudioPlayerInterface(),
                        display=None,
                        video_app=None
                    )
                ),
                api_endpoint=API_ENDPOINT,
                api_access_token=None
            )
        ),
        request=request
    )

    return request_envelope


def create_launch_request() -> LaunchRequest:
    """Creates an launch request."""
    launch_request = LaunchRequest(
        request_id='{}.0'.format(REQUEST_ID_BASE),
        timestamp=datetime.datetime.utcnow(),
        locale='en-US'
    )
    return launch_request


def create_intent_request(round_index: int,
                          user_utterance: str) -> IntentRequest:
    """Creates an intent request."""
    intent_request = IntentRequest(
        request_id='{}.{}'.format(REQUEST_ID_BASE,
                                  round_index),
        timestamp=datetime.datetime.utcnow(),
        locale='en-US',
        dialog_state=None,
        intent=Intent(
            name='ConverseIntent',
            slots=dict(
                Text=Slot(
                    name='Text',
                    value=user_utterance,
                    confirmation_status=SlotConfirmationStatus.NONE,
                    resolutions=Resolutions(
                        resolutions_per_authority=[
                            Resolution(
                                authority='{}.TEXT'.format(RESOLUTION_AUTHORITY_BASE),
                                status=Status(
                                    code=StatusCode.ER_SUCCESS_NO_MATCH
                                )
                            )
                        ]
                    )
                )
            ),
            confirmation_status=IntentConfirmationStatus.NONE
        )
    )
    return intent_request


def send_request(endpoint_url: str,
                 request_envelope: RequestEnvelope) -> ResponseEnvelope:
    """Sends a request to the endpoint and returns the response."""
    serializer = DefaultSerializer()
    r = requests.post(
        endpoint_url,
        json=serializer.serialize(request_envelope),
    )
    response_envelope = serializer.deserialize(
        payload=r.text,
        obj_type=ResponseEnvelope
    )

    return response_envelope


def unescape_ssml(text: str) -> str:
    """Unescapes XML control characters in SSML.

    See:
        https://console.bluemix.net/docs/services/text-to-speech/http.html#escape

        We first unescape the text in case it already contains escaped control
        characters.
    """

    return xml.sax.saxutils.unescape(text, {"&quot;": '"', "&apos;": "'"})


def remove_ssml_tags(text: str) -> str:
    root = etree.fromstring(text)
    text = u' '.join(root.itertext())
    return re.sub(r' +', ' ', text)
