from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging

import boto3
from boto3.session import ResourceNotExistsError

from .dynamodb_utils import (dump_item_to_dynamodb,
                             load_item_from_dynamodb)


logger = logging.getLogger(__file__)


class RoundSaverException(Exception):
    """Class for exceptions raised during the round saver logic."""
    pass


class RoundSaverAdapterBase(ABC):
    """The round saver base (abstract) class.
    """

    def __init__(self):
        pass


    @abstractmethod
    def save_round(self,
                   session_id: str,
                   round_index: int,
                   round_attributes: Dict[str, object]) -> None:
        pass


    @abstractmethod
    def get_round(self,
                  session_id: str,
                  round_index: int,
                  attribute_names: Optional[List[str]]) -> Optional[Dict[str, Any]]:
        pass


class RoundSaver():
    """Save a session round-by-round.

    A round is defined as a user turn and a bot turn.

    Partition key: session id
    Sort key: round index
    """

    def __init__(self,
                 saver_adapter: RoundSaverAdapterBase) -> None:
        """Constructor."""

        if saver_adapter is None:
            raise RoundSaverException("saver_adapter cannot be none!")

        self._saver_adapter = saver_adapter


    def save_round(self,
                   session_id: str,
                   round_index: int,
                   round_attributes: Dict[str, object]) -> None:
        self._saver_adapter.save_round(
            session_id=session_id,
            round_index=round_index,
            round_attributes=round_attributes
        )

    def get_round(self,
                  session_id: str,
                  round_index: int,
                  attribute_names: Optional[List[str]]) -> Optional[Dict[str, Any]]:
        return self._saver_adapter.get_round(
            session_id=session_id,
            round_index=round_index,
            attribute_names=attribute_names
        )


class DynamoDbRoundSaverAdapter(RoundSaverAdapterBase):
    """Round Saver Adapter implementation using AWS DynamoDB.
    """

    def __init__(self,
                 table_name: str,
                 endpoint_url: str) -> None:
        super().__init__()

        self._table_name = table_name
        dynamodb_resource = boto3.resource("dynamodb", endpoint_url=endpoint_url)
        self._create_table_if_not_exists(dynamodb_resource)
        self._table = dynamodb_resource.Table(self._table_name)


    def save_round(self,
                   session_id: str,
                   round_index: int,
                   round_attributes: Dict[str, Any]) -> None:

        logger.debug(
            'DynamoDbRoundSaverAdapter.save_round: %s',
            round_attributes
        )

        # Deals with the following boto3 error for float numbers.
        #   TypeError: Float types are not supported. Use Decimal types instead.
        # See https://github.com/boto/boto3/issues/369
        round_attributes = dump_item_to_dynamodb(round_attributes)
        try:
            self._table.put_item(
                Item={'sessionId': session_id,
                      'roundIndex': round_index,
                      'attributes': round_attributes})
        except ResourceNotExistsError:
            raise RoundSaverException(
                "DynamoDb table {} doesn't exist. "
                "Failed to save round attributes "
                "to DynamoDb table.".format(
                    self._table_name
                )
            )
        except Exception as e:
            raise RoundSaverException(
                "Failed to save round attributes to DynamoDb table. "
                "Exception of type {} occurred: {}".format(
                    type(e).__name__, str(e)
                )
            )


    def get_round(self,
                  session_id: str,
                  round_index: int,
                  attribute_names: Optional[List[str]]) -> Optional[Dict[str, Any]]:
        """Gets the round attributes for the specified attribute names.
        """
        projection_expression: Optional[str] = None
        if attribute_names:
            projection_expression = ','.join([
                'attributes.{}'.format(name)
                for name in attribute_names
            ])
        response = self._table.get_item(
            Key={
                'sessionId': session_id,
                'roundIndex': round_index,
            },
            ProjectionExpression=projection_expression
        )
        data = response.get('Item', {})
        attributes = data.get('attributes', None)
        if attributes is None:
            return None
        return load_item_from_dynamodb(attributes)


    def _create_table_if_not_exists(self,
                                    dynamodb_resource) -> None:
        """Creates table in Dynamodb resource if it doesn't exist.
        """
        try:
            dynamodb_resource.create_table(
                TableName=self._table_name,
                KeySchema=[
                    {
                        'AttributeName': 'sessionId',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'roundIndex',
                        'KeyType': 'RANGE'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'sessionId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'roundIndex',
                        'AttributeType': 'N'
                    }

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 100
                }
            )
        except Exception as e: # pylint: disable=W0703
            if e.__class__.__name__ != "ResourceInUseException":
                raise RoundSaverException(
                    "Create table if not exists request failed: "
                    "Exception of type {} occurred: {}".format(
                        type(e).__name__, str(e)
                    )
                )
