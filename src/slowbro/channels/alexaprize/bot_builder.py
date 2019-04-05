"""Bot builder for the Alexa Prize channel.
"""

from typing import Any, Dict, Optional
import json
import logging

from aiohttp import web
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.skill import Skill
from ask_sdk_model import RequestEnvelope
from slowbro.core.bot_base import BotBase
from slowbro.core.bot_builder_base import BotBuilderBase
from slowbro.core.slowbro_logger import SlowbroLogger

from .request_handlers import (LaunchRequestHandler,
                               IntentRequestHandler,
                               SessionEndedRequestHandler)
from .exception_handlers import DefaultExceptionHandler


logger = logging.getLogger(__name__)


class AlexaPrizeBotBuilder(BotBuilderBase):
    """The bot builder class for the Alexa Prize channel.
    """

    __slots__ = (
        '_bot',
        '_skill',
        '_skill_builder'
    )

    def __init__(self,
                 bot: BotBase,
                 loglevel: int = logging.INFO,
                 logfile: Optional[str] = None) -> None:
        self._bot = bot
        self._skill_builder = SkillBuilder()
        self._skill_builder.request_handlers.extend([
            LaunchRequestHandler(self._bot),
            IntentRequestHandler(self._bot),
            SessionEndedRequestHandler(self._bot),
        ])
        self._skill_builder.add_exception_handler(
            DefaultExceptionHandler(self._bot)
        )

        self._skill = Skill(
            skill_configuration=self._skill_builder.skill_configuration
        )

        super().__init__(loglevel=loglevel,
                         logfile=logfile)


    async def _lambda_function(self,
                               event: RequestEnvelope,
                               context: Any) -> Dict[str, Any]:
        """The AWS Lambda function handler.

        See
        https://github.com/alexa-labs/alexa-skills-kit-sdk-for-python/blob/master/ask-sdk-core/ask_sdk_core/skill_builder.py
        """

        request_envelope = self._skill.serializer.deserialize(
            payload=json.dumps(event),
            obj_type=RequestEnvelope
        )

        slowbro_logger = SlowbroLogger(
            logger=logger,
            request_id=request_envelope.request.request_id
        )

        slowbro_logger.info(
            'Session ID: %s',
            request_envelope.session.session_id
        )

        response_envelope = self._skill.invoke(
            request_envelope=request_envelope,
            context=context
        )

        return self._skill.serializer.serialize(response_envelope)


    async def _server_handler(self,
                              req: web.Request) -> web.Response:
        """The server handler.

        For Alexa Skill, the response Status code is always 200 unless exception
        happens.
        """

        event = await req.json()

        try:
            data = await self._lambda_function(event, {})
            return web.json_response(data)
        except Exception as e:
            raise e
