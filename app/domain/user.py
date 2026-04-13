from dataclasses import dataclass
from datetime import datetime

from app.domain.ids import UserId


@dataclass(frozen=True)
class User:
    id: UserId
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
