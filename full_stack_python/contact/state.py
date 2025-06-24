# guardianslime/full-stack-python/full-stack-python-8c473aa59b63fc9e7a7075ae9cbea38efb6553ed/full_stack_python/contact/state.py

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

    # ¡FUNCIÓN CORREGIDA!
    # Ahora es una función asíncrona que maneja el estado de carga.
    async def list_entries(self):
        """Carga las entradas de contacto y maneja el estado de carga."""
        self.is_loading = True
        yield  # Permite que la UI muestre el indicador de carga

        try:
            # Añadimos una pequeña pausa para que el indicador sea visible
            # incluso en conexiones rápidas, mejorando la experiencia de usuario.
            await asyncio.sleep(0.5)
            with rx.session() as session:
                self.entries = session.exec(
                    rx.select(ContactEntryModel)
                ).all()
        finally:
            # Críticamente, nos aseguramos de que is_loading se ponga en False
            # al final de la operación, para ocultar el indicador de carga.
            self.is_loading = False
            yield