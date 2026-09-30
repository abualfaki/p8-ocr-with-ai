import json
from enum import Enum
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import List, Optional, Annotated, Union


class FooBar(BaseModel):
    count: int
    size: Union[float, None] = None


class Gender(str, Enum):
    male = 'male',
    female = 'female'
    other = 'other'
    not_given = 'not_given'


class MainModel(BaseModel):

    """
    This is the desciption of the main model
    """

    model_config = ConfigDict(title='Main')

    foo: FooBar
    gender: Annotated[Union[Gender, None], Field(alias='Gender')] = None
    snap: int = Field(
        default=42,
        title='The Snap',
        description='this is the value of snap',
        gt=30,
        lt=50,
    )

main_model_schema = MainModel.model_json_schema()

print(json.dumps(main_model_schema, indent=2))