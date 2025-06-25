# full_stack_python/contact_v2/state.py

import reflex as rx
from sqlmodel import select
from ..models import ContactEntryModel
from ..auth.state import SessionState
from ..navigation import routes

class ContactV2State(SessionState):
    """
    Estado para la lista de entradas de contacto.
    Copia la lógica de carga de BlogPostState.
    """
    entries: list[ContactEntryModel] = []

    def list_entries(self):
        """Carga las entradas solo para el usuario autenticado."""
        if not self.is_authenticated or self.my_userinfo_id is None:
            self.entries = []
            return
        with rx.session() as session:
            self.entries = session.exec(
                select(ContactEntryModel).where(
                    ContactEntryModel.userinfo_id == self.my_userinfo_id
                )
            ).all()


class ContactV2FormState(ContactV2State):
    """
    Estado para el formulario de envío.
    Copia la lógica de BlogAddPostFormState.
    """
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        """Maneja el envío del formulario y lo guarda en la base de datos."""
        if not self.is_authenticated or self.my_userinfo_id is None:
            return rx.redirect(routes.LOGIN_ROUTE) # Si no está logueado, no debería poder enviar.

        data = form_data.copy()
        data['userinfo_id'] = self.my_userinfo_id

        try:
            with rx.session() as session:
                db_entry = ContactEntryModel(**data)
                session.add(db_entry)
                session.commit()
        except Exception as e:
            print(f"ERROR AL GUARDAR EL FORMULARIO: {e}")

        # Redirige a la página de entradas para ver el resultado.
        return rx.redirect(routes.CONTACT_ENTRIES_V2_ROUTE)