from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pynamodb.models import Model
from pynamodb.expressions.condition import Comparison
from pydantic import BaseModel


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseDynamoDBRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self._model = model

    def get_all(self) -> List[ModelType]:
        return list(self.model.scan())

    def get(
        self,
        hash_key: Union[str, int, float],
        range_key: Optional[Union[str, int, float, Comparison]] = None,
        filter_condition: Optional[Comparison] = None,
    ) ->  List[ModelType]:
        args = [hash_key]
        if range_key:
            args.append(range_key)
        kwargs = {}
        if filter_condition:
            kwargs['filter_condition'] = filter_condition
        return list(self.model.query(*args, **kwargs))

    def create(
        self,
        *,
        data: CreateSchemaType,
    ) -> ModelType:
        self.model(**data.dict()).save()
