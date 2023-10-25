from datetime import datetime

from pydantic import BaseModel


class UpdateDateTimeSchema(BaseModel):
    last_update: datetime
