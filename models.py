from pydantic import BaseModel
from typing import Optional


class RestaurantContext(BaseModel):

    customer_id: int
    name: str
    table_number: Optional[int] = None
    reservation_date: Optional[str] = None
    reservation_time: Optional[str] = None


class InputGuardRailOutput(BaseModel):

    is_off_topic: bool
    reason: str


class RestaurantOutputGuardRailOutput(BaseModel):

    contains_off_topic: bool
    contains_internal_info: bool
    is_unprofessional: bool
    reason: str


class HandoffData(BaseModel):

    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str
