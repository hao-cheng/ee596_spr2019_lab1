from typing import Dict, Any


class SessionAttributes():
    """Session attributes.
    """


    def __init__(self,
                 round_index: int = 0) -> None:
        """Constructor."""
        self.round_index = round_index


    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'round_index': self.round_index,
        }

        return json_obj


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        self.round_index = json_obj.get('round_index', 0)
