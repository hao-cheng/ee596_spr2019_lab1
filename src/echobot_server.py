"""Server for the Echo Bot via Alexa Channel.
"""

import argparse
import logging

from slowbro.channels.alexaprize import BotBuilder
from bots.echobot.bot import Bot


def main():
    cmdline_parser = argparse.ArgumentParser(
        description=__doc__
    )
    cmdline_parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='host address'
    )
    cmdline_parser.add_argument(
        '--port',
        default='8080',
        help='host port'
    )
    cmdline_parser.add_argument(
        '--dynamodb_endpoint',
        default='http://localhost:8000',
        help='dynamodDB endpoint'
    )
    cmdline_parser.add_argument(
        '--debug',
        default=False,
        action='store_true',
        help='set loglevel to DEBUG'
    )
    args = cmdline_parser.parse_args()

    bot = Bot(
        dynamodb_table_name='echobot-round-attributes',
        dynamodb_endpoint_url=args.dynamodb_endpoint
    )
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    bot_builder = BotBuilder(
        bot=bot,
        loglevel=loglevel
    )
    bot_builder.run_server(args.host,
                           args.port)


if __name__ == '__main__':
    main()
