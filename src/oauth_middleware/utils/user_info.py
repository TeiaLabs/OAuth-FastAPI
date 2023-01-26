from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True, eq=True)
class MasterUserInfo:
    authorizer_identifier: str
    expire_at: float
    issuer: str
    key: str
    scope: int
    user_id: str

    @classmethod
    def from_claims(
        cls, key: str, user_id, claims: Dict[str, Any]
    ) -> "MasterUserInfo":
        obj = cls(key=key, user_id=user_id, **claims)
        return obj


@dataclass(frozen=True, eq=True)
class SlaveUserInfo:
    authorizer_identifier: str
    expire_at: float
    key: str
    scope: int
