"""
SQLAlchemy ORM models for OCT B-Scan Labeler database.
Defines Scan and BScan models with relationships and indexes.
"""

from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Scan(Base):
    """
    Represents an OCT scan/tomogram containing multiple B-scans.

    Attributes:
        scan_id: Unique identifier for the scan (primary key)
        created_at: Timestamp when scan was created
        updated_at: Timestamp when scan was last updated
        bscans: Relationship to associated B-scans
    """
    __tablename__ = "scans"

    scan_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship: one scan has many bscans
    bscans: Mapped[List["BScan"]] = relationship(
        "BScan",
        back_populates="scan",
        cascade="all, delete-orphan",
        order_by="BScan.bscan_index"
    )

    def __repr__(self) -> str:
        return f"<Scan(scan_id='{self.scan_id}', bscans={len(self.bscans)})>"


class BScan(Base):
    """
    Represents a single B-scan image within an OCT scan.

    Attributes:
        id: Auto-incrementing primary key
        scan_id: Foreign key to parent scan
        bscan_index: Index of B-scan within the scan (0-based)
        path: File system path to the B-scan image (unique)
        label: Labeling status (0=unlabeled, 1=healthy, 2=unhealthy)
        updated_at: Timestamp when label was last updated
        scan: Relationship to parent scan
    """
    __tablename__ = "bscans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("scans.scan_id", ondelete="CASCADE"),
        nullable=False
    )
    bscan_index: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    label: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship: many bscans belong to one scan
    scan: Mapped["Scan"] = relationship("Scan", back_populates="bscans")

    # Indexes for efficient querying
    __table_args__ = (
        # Ensure unique (scan_id, bscan_index) combination
        Index("idx_scan_bscan", "scan_id", "bscan_index", unique=True),
        # Index for filtering by scan and label
        Index("idx_scan_label", "scan_id", "label"),
        # Index for global label queries
        Index("idx_label", "label"),
    )

    def __repr__(self) -> str:
        label_str = {0: "unlabeled", 1: "healthy", 2: "unhealthy"}.get(self.label, "unknown")
        return f"<BScan(id={self.id}, scan='{self.scan_id}', index={self.bscan_index}, label='{label_str}')>"

    @property
    def is_labeled(self) -> bool:
        """Check if B-scan has been labeled (not unlabeled)."""
        return self.label in (1, 2)

    @property
    def label_name(self) -> str:
        """Get human-readable label name."""
        return {0: "unlabeled", 1: "healthy", 2: "unhealthy"}.get(self.label, "unknown")
