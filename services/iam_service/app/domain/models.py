import uuid
from sqlalchemy import Column, String, TIMESTAMP, Boolean, VARCHAR, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from services.iam_service.app.core.base import EntityBase


class User(EntityBase):
    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4
    )

    email = Column(VARCHAR(255), unique=True, nullable=False)

    full_name = Column(String(255), nullable=False)

    password_hash = Column(String, nullable=False)

    role = Column(String(20), nullable=False)

    last_login = Column(TIMESTAMP(timezone=True), nullable=True)

    is_verified = Column(Boolean, nullable=False, server_default=text("FALSE"))

    status = Column(
        String(20),
        nullable=False,
        server_default=text("'active'")
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('creator', 'admin')",
            name="check_user_role"
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')",
            name="check_user_status"
        ),
    )
