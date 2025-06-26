# full_stack_python/contact/state.py

from __future__ import annotations
from typing import Optional, List
import reflex as rx

import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import ContactEntryModel, UserInfo

# Definimos la ruta base para las entradas de contacto
CONTACT_ENTRIES_ROUTE = navigation.routes.CONTACT_ENTRIES_ROUTE
if CONTACT_ENTRIES_ROUTE.endswith("/"):
    CONTACT_ENTRIES_ROUTE = CONTACT_ENTRIES_ROUTE[:-1]

class ContactEntryState(SessionState):
    """
    Estado para manejar la lista de entradas de contacto y los detalles.
    (Equivalente a BlogPostState)
    """
    entries: List["ContactEntryModel"] = []
    
    def load_entries(self):
        """Carga todas las entradas de contacto desde la base de datos."""
        with rx.session() as session:
            # La consulta ahora ordena por ID descendente para mostrar las más nuevas primero
            self.entries = session.exec(
                select(ContactEntryModel).order_by(ContactEntryModel.id.desc())
            ).all()

class ContactAddFormState(ContactEntryState):
    """
    Estado para manejar el formulario de creación de una nueva entrada.
    (Equivalente a BlogAddPostFormState)
    """
    form_data: dict = {}
    did_submit: bool = False

    @rx.var
    def thank_you_message(self) -> str:
        """Mensaje de agradecimiento después del envío."""
        first_name = self.form_data.get("first_name", "")
        return f"Thank you, {first_name}!" if first_name else "Thank you for your message!"

    async def handle_submit(self, form_data: dict):
        """Maneja el envío del formulario de contacto."""
        self.form_data = form_data
        with rx.session() as session:
            user_info = self.authenticated_user_info
            
            db_entry = ContactEntryModel(
                first_name=form_data.get("first_name", ""),
                last_name=form_data.get("last_name"),
                email=form_data.get("email"),
                message=form_data.get("message", ""),
                # Asocia la entrada con el usuario si está logueado
                userinfo_id=user_info.id if user_info else None,
            )
            session.add(db_entry)
            session.commit()

        # Muestra el mensaje de agradecimiento
        self.did_submit = True
        yield
        await rx.sleep(3)
        # Oculta el mensaje y resetea el formulario para un nuevo envío
        self.did_submit = False
        yield