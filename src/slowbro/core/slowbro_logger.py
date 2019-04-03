import logging


class SlowbroLogger(logging.LoggerAdapter):
    """Logger adapter for Slowbro.
    """

    def __init__(self,
                 logger: logging.Logger,
                 request_id: str) -> None:
        super().__init__(logger, {})

        self._request_id = request_id


    def process(self, msg, kwargs):
        return '[%s] %s' % (self._request_id, msg), kwargs
