import uuid
from sqlalchemy import DateTime, func, ForeignKey, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

MODE_VALUES = ("resolve","draft","merge")

class AIAction(Base):
    __tablename__ = "ai_actions"
    __table_args__ = (
        CheckConstraint(f"mode in {MODE_VALUES}", name="ai_actions_mode_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id"), index=True, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    fields_modified: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    invoked_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
