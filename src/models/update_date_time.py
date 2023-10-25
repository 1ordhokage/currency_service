from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class UpdateDateTime(Base):
    __tablename__ = "update_date_time"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    last_update: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        nullable=False
    )
