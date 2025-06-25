# full_stack_python/contact/state.py

import reflex as rx
from sqlmodel import select, selectinload
from ..models import ContactEntry, User
from ..auth.state import AuthState

class ContactState(rx.State):
    """
    State for the contact form page.
    """
    form_data: dict = {}
    entries: list[ContactEntry] = []
    
    # Nuevo estado para gestionar la visualización del mensaje de agradecimiento
    submitted: bool = False

    def handle_submit(self, form_data: dict):
        """Handle the form submission.

        Args:
            form_data: The form data.
        """
        self.form_data = form_data
        
        # Obtiene el estado de autenticación para acceder al usuario logueado
        auth_state = self.get_state(AuthState)
        user_id = auth_state.user.id if auth_state.is_logged_in else None

        with rx.session() as session:
            entry = ContactEntry(
                name=self.form_data["name"],
                email=self.form_data["email"],
                message=self.form_data["message"],
                # Guarda el ID del usuario junto con los datos del formulario
                user_id=user_id, 
            )
            session.add(entry)
            session.commit()
            
        # Marca el formulario como enviado para mostrar el mensaje de agradecimiento
        self.submitted = True
        # Limpia los campos del formulario
        self.form_data = {}
        
        # Recarga las entradas para mantener la lista actualizada
        return self.load_entries

    def load_entries(self):
        """Load the contact entries from the database."""
        with rx.session() as session:
            self.entries = session.exec(
                # Usamos selectinload para cargar eficientemente los datos del usuario relacionado
                select(ContactEntry).options(selectinload(ContactEntry.user))
            ).all()
            
    # Nuevo manejador de eventos para reiniciar el formulario
    def reset_form(self):
        """Resetea el estado del formulario para permitir un nuevo envío."""
        self.submitted = False
        self.form_data = {}