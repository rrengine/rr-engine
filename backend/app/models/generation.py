import uuid
from sqlalchemy import DateTime, func, ForeignKey, String, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

SOURCE_VALUES = ("generate","regenerate","import","ai_merge","ai_draft","factory_feedback")

class Generation(Base):
    __tablename__ = "generations"
    __table_args__ = (
        CheckConstraint(f"source in {SOURCE_VALUES}", name="generations_source_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    parent_ids: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
