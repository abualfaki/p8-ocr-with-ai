from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError

class User(BaseModel):
    id: int
    name: str = 'Jane Doe'
    signup_ts: Optional[datetime] = None

    model_config = ConfigDict(str_max_length=10)


# Instantiate Model
m = User.model_validate({'id': 123, 'name': 'James'})
print(m)


try:
    n = User.model_validate({'id': 123, 'name': 'Abu', 'signup_ts': '2026-09-04'})
    print(n.signup_ts)
except ValidationError as e:
    print(e)