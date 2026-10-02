from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, Field

PUBLIC_ROLES = ["farmer", "supply_chain_manager", "distributor", "retailer", "consumer"]


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Full Name")
    email: EmailStr = Field(..., description="User Email")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    role: str = Field(..., description="User Role (public roles only)")

    @validator("role")
    def validate_public_role(cls, v):
        clean_role = v.strip().lower()
        if clean_role == "admin":
            raise ValueError("Public registration cannot create Admin accounts.")
        if clean_role not in PUBLIC_ROLES:
            raise ValueError(f"Invalid role '{v}'. Allowed public roles: {', '.join(PUBLIC_ROLES)}")
        return clean_role


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
