# full_stack_python/contact/state.py

from __future__ import annotations
from typing import List
import reflex as rx
import asyncio
from sqlmodel import select

from ..auth.state import SessionState
from ..models import ContactEntryModel

# --- ESTADO PARA EL FORMULARIO DE AÑADIR (NECESITA LA SESIÓN) ---
class ContactAddFormState(SessionState):
    """
    Estado dedicado para manejar el envío del formulario de contacto.
    Necesita heredar de SessionState para asociar el envío con el usuario.
    """
    form_data: dict = {}
    did_submit: bool = False

    @rx.var
    def thank_you_message(self) -> str:
        first_name = self.form_data.get("first_name", "")
        return f"¡Gracias, {first_name}!" if first_name else "¡Gracias por tu mensaje!"

    async def handle_submit(self, form_data: dict):
        self.form_data = form_data
        with rx.session() as session:
            user_info = self.authenticated_user_info
            db_entry = ContactEntryModel(
                first_name=form_data.get("first_name", ""),
                last_name=form_data.get("last_name"),
                email=form_data.get("email"),
                message=form_data.get("message", ""),
                userinfo_id=user_info.id if user_info else None,
            )
            session.add(db_entry)
            session.commit()

        self.did_submit = True
        yield
        await asyncio.sleep(4)
        self.did_submit = False
        yield

# --- ESTADO PARA EL HISTORIAL (NO NECESITA LA SESIÓN DIRECTAMENTE) ---
class ContactHistoryState(rx.State):
    """
    Estado simple y aislado para mostrar el historial de entradas.
    No hereda de SessionState para evitar conflictos.
    """
    entries: List[ContactEntryModel] = []

    def load_entries(self):
        """Carga TODAS las entradas de la base de datos."""
        with rx.session() as session:
            self.entries = session.exec(
                select(ContactEntryModel).order_by(ContactEntryModel.id.desc())
            ).all()