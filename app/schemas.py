from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name is required")
        return value


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    balance: float
    created_at: datetime


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["credit", "debit"]
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    description: str = Field(min_length=1, max_length=255)

    @field_validator("description")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    type: str
    amount: float
    description: str
    reference_id: str
    created_at: datetime


class BalanceResponse(BaseModel):
    account_id: int
    balance: float


class TransactionHistoryResponse(BaseModel):
    items: list[TransactionResponse]
    page: int
    page_size: int
    total_records: int
    total_pages: int
