from typing import Any, Dict, List, Optional
import logging


logger = logging.getLogger(__name__)


class AsrHypothesisToken():
    """The Automatic Speech Recognition hypothesis token.
    """

    def __init__(self,
                 value: str = '',
                 confidence: float = 0,
                 start_offset: int = -1,
                 end_offset: int = -1) -> None:
        self.value = value
        self.confidence = confidence
        # startOffsetInMilliseconds
        self.start_offset = start_offset
        # endOffsetInMilliseconds
        self.end_offset = end_offset


    def to_dict(self) -> Dict[str, Any]:
        json_obj = {
            'value': self.value,
            'confidence': self.confidence,
            'start_offset': self.start_offset,
            'end_offset': self.end_offset
        }
        return json_obj


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        self.value = json_obj.get('value', '')
        self.confidence = json_obj.get('confidence', 0)
        self.start_offset = json_obj.get('start_offset', -1)
        self.end_offset = json_obj.get('end_offset', -1)


class AsrHypothesisUtterance():
    """The Automatic Speech Recognition hypothesis utterance.
    """

    def __init__(self,
                 tokens: Optional[List[AsrHypothesisToken]] = None,
                 confidence: float = 0) -> None:
        self.tokens = tokens
        self.confidence = confidence


    def __str__(self) -> str:
        if self.tokens is None:
            return ''

        return ' '.join([
            token.value
            for token in self.tokens
        ])


    def to_dict(self) -> Dict[str, Any]:
        assert self.tokens is not None
        json_obj = {
            'tokens': [
                token.to_dict()
                for token in self.tokens
            ],
            'confidence': self.confidence
        }
        return json_obj


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        self.tokens = []
        for item in json_obj.get('tokens', []):
            token = AsrHypothesisToken()
            token.from_dict(item)
            self.tokens.append(token)

        self.confidence = json_obj.get('confidence', 0)


class UserMessage():
    """The UserMessage container.
    """

    def __init__(self,
                 payload: Optional[Dict[str, Any]] = None,
                 channel: str = '',
                 request_id: str = '',
                 session_id: str = '',
                 user_id: str = '',
                 text: str = '',
                 asr_hypos: Optional[List[
                     AsrHypothesisUtterance
                 ]] = None) -> None:
        self.payload = payload
        self.channel = channel
        self.request_id = request_id
        self.session_id = session_id
        self.user_id = user_id
        self.text = text
        self.asr_hypos = asr_hypos


    def to_dict(self) -> Dict[str, Any]:
        """Serializes the object."""
        json_obj: Dict[str, Any] = {
            'channel': self.channel,
            'request_id': self.request_id,
            'session_id': self.session_id,
            'text': self.text,
        }
        if self.payload:
            json_obj['payload'] = self.payload
        if self.asr_hypos:
            json_obj['asr_hypos'] = [
                hypo.to_dict()
                for hypo in self.asr_hypos
            ]
        return json_obj


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        """Deserializes the object."""
        self.payload = json_obj.get('payload', None)
        self.channel = json_obj.get('channel', '')
        self.request_id = json_obj.get('request_id', '')
        self.session_id = json_obj.get('session_id', '')
        self.text = json_obj.get('text', '')
        self.asr_hypos = []
        for item in json_obj.get('asr_hypos', []):
            hypo = AsrHypothesisUtterance()
            hypo.from_dict(item)
            self.asr_hypos.append(hypo)


    def get_utterance(self) -> str:
        """Gets the utterance.

        If asr_hypos is available, we use asr_hypos[0].
        Otherwise, we use text.
        """
        if self.asr_hypos:
            return self.asr_hypos[0].__str__()

        return self.text
