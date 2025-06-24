# full_stack_python/models.py
from __future__ import annotations
from typing import Optional
import reflex as rx
from sqlmodel import Field

class UserInfoModel(rx.Model, table=True):
    # ... (Tu modelo de usuario se queda como está)
    username: str = Field(unique=True, index=True)
    password_hash: str
    enabled: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ContactEntryModel(rx.Model, table=True):
    # ¡CORRECCIÓN! Hacemos 'last_name' y 'email' explícitamente opcionales
    # para que coincida con la lógica del formulario y evitar errores.
    first_name: str
    last_name: Optional[str]
    email: Optional[str] 
    message: str
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfomodel.id")