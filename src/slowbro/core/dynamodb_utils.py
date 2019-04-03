from typing import Any, Dict, List
import logging
from collections.abc import Iterable, Mapping, ByteString, Set
import numbers
import decimal


logger = logging.getLogger(__file__)

CONTEXT = decimal.Context(
    Emin=-128,
    Emax=126,
    # rounding=None,
    prec=38,
    traps=[decimal.Clamped, decimal.Overflow, decimal.Underflow]
)

def dump_item_to_dynamodb(item: Any) -> Any:
    """Replaces float with Decimal.

    Deals with the following boto3 error for float numbers.
        TypeError: Float types are not supported. Use Decimal types instead.
    See https://github.com/boto/boto3/issues/369 for details.
    """

    if isinstance(item, str):
        if not item:
            # an AttributeValue may not contain an empty string
            return None
        return item
    # don't catch str/bytes with Iterable check below;
    # don't catch bool with numbers.Number
    if isinstance(item, (ByteString, bool)):
        return item
    # don't catch integers with numbers.Number
    if isinstance(item, numbers.Integral):
        return item

    # ignores inexact, rounding errors
    if isinstance(item, numbers.Number):
        return CONTEXT.create_decimal(item) # type: ignore

    # mappings are also Iterable
    data: Any
    if isinstance(item, Mapping):
        data = dict()
        for key, value in item.items():
            value = dump_item_to_dynamodb(value)
            if value is None:
                continue
            data[key] = value
        if not data:
            return None
        return data

    # boto3's dynamodb.TypeSerializer checks isinstance(o, Set)
    # so we can't handle this as a list
    if isinstance(item, Set):
        data = set(map(dump_item_to_dynamodb, item))
        if not data:
            return None
        return data

    # may not be a literal instance of list
    if isinstance(item, Iterable):
        data = list(map(dump_item_to_dynamodb, item))
        if not data:
            return None
        return data

    # datetime, custom object, None
    return item


def load_item_from_dynamodb(item: Any) -> Any:
    """Replaces Decimal with float.

    Deals with the following boto3 error for float numbers.
        TypeError: Float types are not supported. Use Decimal types instead.
    See https://github.com/boto/boto3/issues/369 for details.
    """
    if isinstance(item, str):
        if not item:
            return None
        return item
    if isinstance(item, (ByteString, bool)):
        return item
    if isinstance(item, numbers.Integral):
        return item

    if isinstance(item, decimal.Decimal):
        return float(item)

    # mappings are also Iterable
    if isinstance(item, Mapping):
        return {
            key: load_item_from_dynamodb(value)
            for key, value in item.items()
        }

    # boto3's dynamodb.TypeSerializer checks isinstance(o, Set)
    # so we can't handle this as a list
    if isinstance(item, Set):
        return set(map(load_item_from_dynamodb, item))

    # may not be a literal instance of list
    if isinstance(item, Iterable):
        return list(map(load_item_from_dynamodb, item))

    # datetime, custom object, None
    return item


def batch_get_items_wrapper(request_items: Dict[str, Dict[str, Dict[str, Any]]],
                            dynamodb_client: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Retrieves multiple items with retries.
    """

    try:
        output = dynamodb_client.batch_get_item(
            RequestItems=request_items
        )
    except:
        # TODO: backoff when throttling
        logger.warning(
            'batch retrieve items failed: %s',
            request_items
        )
        return {}

    responses = output.get('Responses', {})
    unprocessed_items = output.get('UnprocessedKeys', {})
    if unprocessed_items:
        # TODO: backoff when throttling
        result = batch_get_items_wrapper(unprocessed_items, dynamodb_client)
        for key, value in result.items():
            if key in responses:
                responses[key] += value
            else:
                responses[key] = value

    return responses
