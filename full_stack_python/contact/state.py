# full_stack_python/contact/state.py

from __future__ import annotations
import asyncio
import reflex as rx

from ..auth.state import SessionState
from ..models import ContactEntryModel

class ContactState(SessionState):
    """El estado para manejar el formulario de contacto."""

    form_data: dict = {}
    entries: list[ContactEntryModel] = []
    did_submit: bool = False

    @rx.var
    def thank_you(self) -> str:
        """Un componente que se muestra después de enviar el formulario."""
        first_name = self.form_data.get("first_name", "")
        if first_name:
            return f"Thank you, {first_name}!"
        return "Thank you for your message!"

    async def hydrate_session(self):
        """
        Este evento se ejecuta en on_load para asegurar que authenticated_user_info
        esté disponible antes de que otros eventos como list_entries se ejecuten.
        """
        # No se necesita código aquí, su ejecución en la cadena de eventos es suficiente.
        yield

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
        await asyncio.sleep(3)
        self.did_submit = False
        self.form_data = {}

    async def list_entries(self):
        """Carga las entradas de contacto solo para el usuario autenticado."""
        user_info = self.authenticated_user_info
        if not user_info:
            self.entries = []
            return

        with rx.session() as session:
            self.entries = session.exec(
                rx.select(ContactEntryModel).where(ContactEntryModel.userinfo_id == user_info.id)
            ).all()