from datetime import datetime
from pydantic import BaseModel, Field


class ParsedExpense(BaseModel):
    description: str
    amount: float = Field(gt=0)
    currency: str = "ARS"


class TelegramInfo(BaseModel):
    chat_id: int | None = None
    user_id: int | None = None
    username: str | None = None


class EventMetadata(BaseModel):
    schema_version: int
    parsed_at: datetime


class ParsedExpenseEvent(BaseModel):
    event_id: str
    event_type: str
    event_time: datetime
    source: str
    raw_event_id: str
    telegram: TelegramInfo
    expense: ParsedExpense
    metadata: EventMetadata