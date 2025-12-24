import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, func, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import EntityBase

class Survey(EntityBase):
    __tablename__ = "surveys"

    survey_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4
    )
    creator_id = Column(
    UUID(as_uuid=True),
    ForeignKey("users.user_id", ondelete="CASCADE"),
    nullable=False
)

    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False,index=True)
    public_code = Column(String(12), unique=True, nullable=True, index=True)
    is_public = Column(Boolean, nullable=False,server_default=text("false"))
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
    is_deleted = Column(
        Boolean,
        nullable=False,
        server_default=text("false")
    )

    deleted_at = Column(
    TIMESTAMP(timezone=True),
    nullable=True)

    