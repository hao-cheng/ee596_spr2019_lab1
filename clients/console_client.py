#!/usr/bin/env python3

import os
import sys
import argparse
import codecs
import json

from ask_sdk_core.serialize import DefaultSerializer
from alexa_utils import (create_launch_request,
                         create_intent_request,
                         create_request_envelope,
                         send_request,
                         unescape_ssml)


def main():
    cmdline_parser = argparse.ArgumentParser(
        description=__doc__
    )
    cmdline_parser.add_argument(
        '--endpoint_url',
        default='http://localhost:8080',
        help='endpoint_url'
    )
    cmdline_parser.add_argument(
        '--logdir',
        required=True,
        help='log directory'
    )
    args = cmdline_parser.parse_args()

    serializer = DefaultSerializer()

    if not os.path.exists(args.logdir):
        os.mkdir(args.logdir)


    curr_request = create_launch_request()
    curr_session_attributes: Dict[str, Any] = {}
    round_index = 1
    while True:
        request_envelope = create_request_envelope(
            curr_session_attributes,
            curr_request
        )

        request_json = os.path.join(
            args.logdir,
            'request.round_{}.json'.format(round_index)
        )
        fp = codecs.open(
            request_json,
            'w',
            encoding='utf-8'
        )
        fp.write(json.dumps(serializer.serialize(request_envelope)))
        fp.write('\n')
        fp.close()

        response_envelope = send_request(
            args.endpoint_url,
            request_envelope
        )
        response = response_envelope.response
        if response.should_end_session:
            print('=' * 8, 'Session Ended', '=' * 8)
            print(curr_session_attributes)
            break

        print('=' * 8, 'Round Index:', round_index, '=' * 8 )
        print('Bot Utterance: ',
              unescape_ssml(response.output_speech.ssml[7:-8]))
        if response.reprompt:
            print('Bot Reprompt: ',
                  unescape_ssml(response.reprompt.output_speech.ssml[7:-8]))


        round_index += 1
        user_utterance = input('User Utterance: ')
        curr_session_attributes = response_envelope.session_attributes
        curr_request = create_intent_request(
            round_index=round_index,
            user_utterance=user_utterance,
        )


if __name__ == '__main__':
    main()
