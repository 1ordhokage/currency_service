from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Currency(Base):
    __tablename__ = "currencies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    rate: Mapped[float] = mapped_column(Float(precision=6), nullable=False)
