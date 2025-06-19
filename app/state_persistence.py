from sqlalchemy.orm import Session
from models import AccessGrant, SuccessfulSpellIP


class AccessStateDB:
    def __init__(self, session: Session):
        self.session = session

    def __setitem__(self, uuid: str, value: bool) -> None:
        obj = self.session.get(AccessGrant, uuid)
        if obj:
            obj.granted = value
        else:
            obj = AccessGrant(uuid=uuid, granted=value)
            self.session.add(obj)
        self.session.commit()

    def get(self, uuid: str, default=None):
        obj = self.session.get(AccessGrant, uuid)
        if obj is None:
            return default
        return obj.granted


class SuccessfulSpellIPsDB:
    def __init__(self, session: Session):
        self.session = session

    def __contains__(self, ip: str) -> bool:
        return self.session.get(SuccessfulSpellIP, ip) is not None

    def __setitem__(self, ip: str, value: dict) -> None:
        obj = self.session.get(SuccessfulSpellIP, ip)
        if obj:
            obj.user_uuid = value.get("user_uuid")
            obj.cast_time = value.get("cast_time")
        else:
            obj = SuccessfulSpellIP(
                ip=ip,
                user_uuid=value.get("user_uuid"),
                cast_time=value.get("cast_time"),
            )
            self.session.add(obj)
        self.session.commit()
