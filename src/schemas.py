from pydantic import BaseModel
from typing import Optional

# Schema for creating a user
class UserCreate(BaseModel):
    email: str
    password: str
    role: str
    designation: str
    company: str
    first_name: str
    last_name: str


# Schema for updating a user
class UserUpdate(BaseModel):
    email: str = None
    password: str = None
    role: str = None
    designation: str = None
    company: str = None
    first_name: str = None
    last_name: str = None
    

# Schema for allowing Admin to update any other user
class AdminUserUpdate(BaseModel):
    email : str = None
    role: str = None
    

# Schema for allowing Admin to delete any other user
class AdminUserDelete(BaseModel):
    email : str = None
    

# Token data schema
class TokenData(BaseModel):
    email: Optional[str] = None