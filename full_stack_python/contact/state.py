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
        return f"Thank you for your message, {first_name}!" if first_name else "Thank you!"

    async def handle_submit(self, form_data: dict):
        """Maneja el envío del formulario, guarda en la BD y refresca la lista."""
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

        # Muestra el mensaje de agradecimiento
        self.did_submit = True
        yield

        # Espera 3 segundos
        await asyncio.sleep(3)

        # Oculta el mensaje de agradecimiento y limpia el formulario
        self.did_submit = False
        self.form_data = {}
        yield

    async def list_entries(self):
        """Carga las entradas de contacto y maneja el estado de carga."""
        self.is_loading = True
        yield
        try:
            with rx.session() as session:
                self.entries = session.exec(
                    rx.select(ContactEntryModel).order_by(ContactEntryModel.id.desc())
                ).all()
        finally:
            await asyncio.sleep(0.25) # Pequeña pausa para fluidez
            self.is_loading = False
            yield