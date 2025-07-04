# full_stack_python/contact/state.py

from __future__ import annotations
import asyncio
import reflex as rx
from sqlmodel import select

# Se importa SessionState para poder acceder al usuario autenticado
from ..auth.state import SessionState
from ..models import ContactEntryModel, UserInfo

class ContactState(SessionState):
    """
    Un único estado simple que maneja tanto el formulario como la lista de entradas.
    """
    # Para el formulario
    form_data: dict = {}
    did_submit: bool = False

    # Para la lista de entradas
    entries: list[ContactEntryModel] = []

    # --- ¡NUEVO MÉTODO COMPUTADO! ---
    @rx.var
    def entries_with_formatted_date(self) -> list[dict]:
        """
        Toma la lista de entradas y devuelve una nueva lista de diccionarios
        con la fecha de creación ya formateada como un string.
        """
        processed_entries = []
        for entry in self.entries:
            # Convierte el modelo a un diccionario y añade el campo formateado
            entry_dict = entry.dict()
            entry_dict["created_at_formatted"] = entry.created_at.strftime("%Y-%m-%d %H:%M")
            processed_entries.append(entry_dict)
        return processed_entries
    # --------------------------------

    @rx.var
    def thank_you_message(self) -> str:
        """Mensaje de agradecimiento."""
        first_name = self.form_data.get("first_name", "")
        return f"¡Gracias, {first_name}!" if first_name else "¡Gracias por tu mensaje!"

    async def handle_submit(self, form_data: dict):
        # ... (Este método no cambia)
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
