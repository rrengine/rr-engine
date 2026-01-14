import uuid
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class MergeHistory(Base):
    __tablename__ = "merge_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merged_generation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id"), index=True, nullable=False)
    parent_a: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id"), nullable=False)
    parent_b: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id"), nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
