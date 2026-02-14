"""
Pydantic schemas for request/response validation in OCT B-Scan Labeler API.
Defines data transfer objects (DTOs) for scans, B-scans, and statistics.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ===== B-SCAN SCHEMAS =====

class BScanBase(BaseModel):
    """Base schema for B-scan with common fields."""
    bscan_index: int = Field(..., ge=0, description="Index of B-scan within scan (0-based)")
    label: int = Field(default=0, ge=0, le=2, description="Label: 0=unlabeled, 1=healthy, 2=unhealthy")


class BScanCreate(BScanBase):
    """Schema for creating a new B-scan."""
    scan_id: str = Field(..., min_length=1, description="Parent scan ID")
    path: str = Field(..., min_length=1, description="File path to B-scan image")


class BScanResponse(BScanBase):
    """Schema for B-scan response with full details."""
    id: int = Field(..., description="B-scan ID")
    scan_id: str = Field(..., description="Parent scan ID")
    path: str = Field(..., description="File path to B-scan image")
    updated_at: datetime = Field(..., description="Last update timestamp")
    preview_url: Optional[str] = Field(None, description="URL to preview image")
    prev_index: Optional[int] = Field(None, description="Index of previous B-scan (null if first)")
    next_index: Optional[int] = Field(None, description="Index of next B-scan (null if last)")
    next_unlabeled_index: Optional[int] = Field(None, description="Index of next unlabeled B-scan")

    class Config:
        from_attributes = True


class BScanLabelUpdate(BaseModel):
    """Schema for updating B-scan label."""
    label: int = Field(..., ge=1, le=2, description="New label: 1=healthy, 2=unhealthy")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: int) -> int:
        """Ensure label is either 1 (healthy) or 2 (unhealthy)."""
        if v not in (1, 2):
            raise ValueError("Label must be 1 (healthy) or 2 (unhealthy)")
        return v


# ===== SCAN SCHEMAS =====

class ScanBase(BaseModel):
    """Base schema for scan with common fields."""
    scan_id: str = Field(..., min_length=1, description="Unique scan identifier")


class ScanCreate(ScanBase):
    """Schema for creating a new scan."""
    pass


class ScanStats(BaseModel):
    """Schema for scan statistics."""
    total_bscans: int = Field(..., ge=0, description="Total number of B-scans")
    labeled: int = Field(..., ge=0, description="Number of labeled B-scans")
    unlabeled: int = Field(..., ge=0, description="Number of unlabeled B-scans")
    healthy: int = Field(..., ge=0, description="Number of healthy B-scans")
    unhealthy: int = Field(..., ge=0, description="Number of unhealthy B-scans")
    percent_complete: float = Field(..., ge=0.0, le=100.0, description="Completion percentage")


class ScanResponse(ScanBase):
    """Schema for scan response with statistics."""
    created_at: datetime = Field(..., description="Scan creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    stats: ScanStats = Field(..., description="Scan labeling statistics")

    class Config:
        from_attributes = True


class ScanListResponse(BaseModel):
    """Schema for list of scans response."""
    scans: List[ScanResponse] = Field(..., description="List of scans with statistics")
    total_scans: int = Field(..., ge=0, description="Total number of scans")


# ===== STATISTICS SCHEMAS =====

class GlobalStats(BaseModel):
    """Schema for global statistics across all scans."""
    total_scans: int = Field(..., ge=0, description="Total number of scans")
    total_bscans: int = Field(..., ge=0, description="Total number of B-scans")
    total_labeled: int = Field(..., ge=0, description="Total labeled B-scans")
    total_unlabeled: int = Field(..., ge=0, description="Total unlabeled B-scans")
    total_healthy: int = Field(..., ge=0, description="Total healthy B-scans")
    total_unhealthy: int = Field(..., ge=0, description="Total unhealthy B-scans")
    percent_complete: float = Field(..., ge=0.0, le=100.0, description="Overall completion percentage")


# ===== NAVIGATION SCHEMAS =====

class NavigationMode(BaseModel):
    """Schema for navigation mode configuration."""
    mode: str = Field(
        default="index",
        pattern="^(index|unlabeled)$",
        description="Navigation mode: 'index' (sequential) or 'unlabeled' (skip labeled)"
    )


# ===== ERROR SCHEMAS =====

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")


# ===== HELPER FUNCTIONS =====

def calculate_percent_complete(labeled: int, total: int) -> float:
    """Calculate completion percentage."""
    if total == 0:
        return 0.0
    return round((labeled / total) * 100, 2)


# ===== AUTH SCHEMAS =====

class UserRegister(BaseModel):
    """Schema for user registration (admin-only)."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=4, max_length=128)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Schema for user data in responses (no password)."""
    id: int
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=4, max_length=128)


class AuthStatusResponse(BaseModel):
    """Schema for auth status check."""
    authenticated: bool
    user: Optional[UserResponse] = None


# ===== USER SETTINGS SCHEMAS =====

class UserSettingsResponse(BaseModel):
    """Schema for user settings response."""
    auto_advance: bool
    hotkey_healthy: str
    hotkey_unhealthy: str
    hotkey_next: str
    hotkey_prev: str

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    """Schema for partial settings update."""
    auto_advance: Optional[bool] = None
    hotkey_healthy: Optional[str] = Field(None, max_length=20)
    hotkey_unhealthy: Optional[str] = Field(None, max_length=20)
    hotkey_next: Optional[str] = Field(None, max_length=20)
    hotkey_prev: Optional[str] = Field(None, max_length=20)
