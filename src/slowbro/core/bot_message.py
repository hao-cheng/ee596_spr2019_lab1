from typing import Optional, Dict, Any


class BotMessage():
    """Bot Message container.
    """


    def __init__(self,
                 response_ssml: Optional[str] = None,
                 reprompt_ssml: Optional[str] = None,
                 card_title: Optional[str] = None,
                 card_content: Optional[str] = None,
                 should_end_session: bool = False) -> None:
        self.response_ssml = response_ssml
        self.reprompt_ssml = reprompt_ssml
        self.card_title = card_title
        self.card_content = card_content
        self.should_end_session = should_end_session


    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {}
        if self.response_ssml:
            json_obj['response_ssml'] = self.response_ssml
        if self.reprompt_ssml:
            json_obj['reprompt_ssml'] = self.reprompt_ssml
        if self.card_title:
            json_obj['card_title'] = self.card_title
        if self.card_content:
            json_obj['card_content'] = self.card_content
        json_obj['should_end_session'] = self.should_end_session
        return json_obj


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        self.response_ssml = json_obj.get(
            'response_ssml',
            None
        )
        self.reprompt_ssml = json_obj.get(
            'reprompt_ssml',
            None
        )
        self.card_title = json_obj.get(
            'card_title',
            None
        )
        self.card_content = json_obj.get(
            'card_content',
            None
        )
        self.should_end_session = bool(json_obj.get('should_end_session', False))
