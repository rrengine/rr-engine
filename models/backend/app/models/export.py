import uuid
from sqlalchemy import DateTime, func, ForeignKey, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

PROFILE_VALUES = ("factory","supplier","internal")

class ExportRecord(Base):
    __tablename__ = "exports"
    __table_args__ = (
        CheckConstraint(f"profile in {PROFILE_VALUES}", name="exports_profile_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id"), index=True, nullable=False)
    profile: Mapped[str] = mapped_column(String, nullable=False)
    formats: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    export_uri: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
