from typing import Dict, Any, Optional

from slowbro.core.user_message import UserMessage
from slowbro.core.bot_message import BotMessage


class RoundAttributes():
    """Round attributes.

    Stores necessary information for a single round.
    """

    def __init__(self,
                 round_index: int = 0,
                 user_message: Optional[UserMessage] = None,
                 bot_message: Optional[BotMessage] = None) -> None:
        self.round_index = round_index
        self.user_message = user_message
        self.bot_message = bot_message


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        self.round_index = json_obj.get('round_index', 0)
        self.user_message = None
        if 'user_message' in json_obj:
            self.user_message = UserMessage()
            self.user_message.from_dict(
                json_obj.get('user_message', {})
            )
        self.bot_message = None
        if 'bot_message' in json_obj:
            self.bot_message = BotMessage()
            self.bot_message.from_dict(
                json_obj.get('bot_message', {})
            )


    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'round_index': self.round_index,
        }
        if self.user_message is not None:
            json_obj['user_message'] = self.user_message.to_dict()
        if self.bot_message:
            json_obj['bot_message'] = self.bot_message.to_dict()

        return json_obj
