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
        [cite_start]first_name = self.form_data.get("first_name", "") [cite: 421]
        if first_name:
            return f"Thank you, {first_name}!"
        [cite_start]return "Thank you for your message!" [cite: 422]

    # ¡CORRECCIÓN! El manejador de eventos ahora es asíncrono y usa 'yield'.
    async def handle_submit(self, form_data: dict):
        """Maneja el envío del formulario de manera más robusta."""
        self.form_data = form_data

        with rx.session() as session:
            user_info = self.authenticated_user_info
            
            db_entry = ContactEntryModel(
                [cite_start]first_name=form_data.get("first_name", ""), [cite: 423]
                [cite_start]last_name=form_data.get("last_name"), [cite: 423]
                [cite_start]email=form_data.get("email"), [cite: 423]
                [cite_start]message=form_data.get("message", ""), [cite: 423]
                [cite_start]userinfo_id=user_info.id if user_info else None, [cite: 423]
            )
            session.add(db_entry)
            [cite_start]session.commit() [cite: 424]
            # Esta línea confirma que el objeto se guardó en la DB y actualiza 'db_entry' con los datos de la DB (como el ID).
            # Si el commit falla, esto lanzará un error, haciendo el fallo visible.
            session.refresh(db_entry)

        # Muestra el mensaje de agradecimiento inmediatamente.
        self.did_submit = True
        yield

        # Espera 3 segundos.
        await asyncio.sleep(3)

        # Oculta el mensaje y limpia el formulario.
        self.did_submit = False
        self.form_data = {}
        yield

    def list_entries(self):
         """Carga todas las entradas de contacto desde la base de datos."""
         with rx.session() as session:
                self.entries = session.exec(
                    rx.select(ContactEntryModel).order_by(ContactEntryModel.id.desc())
                ).all()