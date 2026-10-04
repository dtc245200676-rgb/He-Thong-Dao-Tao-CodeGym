from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.role import user_roles


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False, default="")
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(30), nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # Kept for compatibility with the first S1-01 database version.
    # Authorization uses the many-to-many roles relationship below.
    role = Column(String(50), nullable=False, default="student")

    status = Column(String(20), nullable=False, default="active", index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    must_change_password = Column(Boolean, nullable=False, default=False)
    needs_handover = Column(Boolean, nullable=False, default=False)

    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
    sessions = relationship(
        "AuthSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
