# full_stack_python/contact/state.py

from __future__ import annotations
import asyncio
import reflex as rx
from sqlmodel import select

# Se importa SessionState para poder acceder al usuario autenticado
from ..auth.state import SessionState
from ..models import ContactEntryModel

class ContactState(SessionState):
    """
    Un único estado simple que maneja tanto el formulario como la lista de entradas.
    Basado en la lógica original que sí funcionaba.
    """
    # Para el formulario
    form_data: dict = {}
    did_submit: bool = False

    # Para la lista de entradas
    entries: list[ContactEntryModel] = []

    @rx.var
    def thank_you_message(self) -> str:
        """Mensaje de agradecimiento."""
        first_name = self.form_data.get("first_name", "")
        return f"¡Gracias, {first_name}!" if first_name else "¡Gracias por tu mensaje!"

    async def handle_submit(self, form_data: dict):
        """Maneja el envío del formulario."""
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

    def load_entries(self):
        """Carga TODAS las entradas de la base de datos."""
        with rx.session() as session:
            self.entries = session.exec(
                select(ContactEntryModel).order_by(ContactEntryModel.id.desc())
            ).all()