from pydantic import BaseModel


class UserContext(BaseModel):
    token: str
    org_id: int
    role: str
    username: str | None = None

    @property
    def is_admin(self) -> bool:
        return self.role.lower() == "admin"
