from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from models.user import UserRole

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    full_name: Optional[str] = None
    password: Optional[constr(min_length=8)] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_verified: bool
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    token_type: str
    refresh_token: str

class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None 