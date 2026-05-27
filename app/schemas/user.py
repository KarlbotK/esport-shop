from pydantic import Field
from typing import Optional

from app.schemas.common import CommonBase


class LoginDTO(CommonBase):
    username: str
    password: str


class RegisterDTO(CommonBase):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None


class LoginVO(CommonBase):
    token: str
    username: str
    role: str


class UserProfileVO(CommonBase):
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    favorite_category: Optional[str] = None
    browse_count: int = 0
    browse_count_7d: int = 0
    purchasing_power: str = "no purchases"
    total_spending: float = 0.0
    order_count: int = 0
    activity_level: str = "low"
