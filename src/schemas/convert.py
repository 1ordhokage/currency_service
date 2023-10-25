from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ConvertSchema(BaseModel):
    original_code: str
    target_code: str
    amount: float = Field(ge=0)

    @field_validator("original_code", "target_code")
    @classmethod
    def validate_code(cls, value: str):
        if not value.isalpha():
            raise ValueError("The code must contain only letters.")
        if not len(value) == 3:
            raise ValueError("The code's lenght must be 3.")
        return value.upper()


class ConvertResponseSchema(ConvertSchema):
    result: float = Field(ge=0)
    date_time: datetime = datetime.now()
