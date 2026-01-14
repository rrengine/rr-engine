import uuid
from sqlalchemy import DateTime, func, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class GeometryAsset(Base):
    __tablename__ = "geometry_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id"), index=True, nullable=False, unique=True)
    mesh_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    anchors_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    bounds: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    geometry_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
