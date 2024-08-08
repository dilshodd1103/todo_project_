from datetime import datetime

from sqlalchemy import func, types
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class AbstractBase(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(types.String(26), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=datetime.now)