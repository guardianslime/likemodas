# full_stack_python/contact/state.py

import reflex as rx
from sqlmodel import select
# Se ha eliminado la importación de 'selectinload' que causaba el error
from ..models import ContactEntry, User
from ..auth.state import AuthState
from typing import Dict, List

class ContactState(rx.State):
    """
    State for the contact form page.
    """
    form_data: Dict = {}
    entries: List[ContactEntry] = []
    submitted: bool = False

    def handle_submit(self, form_data: Dict):
        """Handle the form submission."""
        self.form_data = form_data
        auth_state = self.get_state(AuthState)
        user_id = auth_state.user.id if auth_state.is_logged_in else None

        with rx.session() as session:
            entry = ContactEntry(
                name=self.form_data["name"],
                email=self.form_data["email"],
                message=self.form_data["message"],
                user_id=user_id,
            )
            session.add(entry)
            session.commit()
        
        self.submitted = True
        self.form_data = {}
        return self.load_entries

    def load_entries(self):
        """Load the contact entries from the database."""
        with rx.session() as session:
            # Se ha eliminado la parte .options(selectinload(...)) para resolver el error.
            self.entries = session.exec(select(ContactEntry)).all()
            
    def reset_form(self):
        """Resets the form state to allow a new submission."""
        self.submitted = False
        self.form_data = {}