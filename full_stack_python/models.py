# full_stack_python/models.py
import reflex as rx
from sqlmodel import Field, Relationship
from typing import List, Union

class User(rx.Model, table=True):
    """User model."""
    id: Union[int, None] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    enabled: bool = True
    contact_entries: List["ContactEntry"] = Relationship(back_populates="user")

class ContactEntry(rx.Model, table=True):
    """Contact entry model."""
    id: Union[int, None] = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str
    user_id: Union[int, None] = Field(default=None, foreign_key="user.id")
    user: Union["User", None] = Relationship(back_populates="contact_entries")

class Blog(rx.Model, table=True):
    """Blog model."""
    id: Union[int, None] = Field(default=None, primary_key=True)
    author: str
    title: str
    content: str
    created_at: str
    updated_at: str