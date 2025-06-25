# full_stack_python/contact/state.py

from __future__ import annotations
import asyncio
import reflex as rx

from .. import navigation
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
        """Asegura que la sesión del usuario esté cargada."""
        yield

    async def handle_submit(self, form_data: dict):
        """Maneja el envío del formulario."""
        self.form_data = form_data
        
        try:
            with rx.session() as session:
                
                # --- ARREGLO DEFINITIVO ---
                # Usamos self.my_userinfo_id, que es la forma segura y consistente
                # (igual que en el blog) para asegurar que asociamos el formulario al usuario.
                user_id = self.my_userinfo_id
                
                print(f"--- INTENTANDO GUARDAR FORMULARIO ---")
                print(f"Datos: {form_data}")
                print(f"ID de Usuario a asociar: {user_id}")
                
                db_entry = ContactEntryModel(
                    first_name=form_data.get("first_name", ""),
                    last_name=form_data.get("last_name"),
                    email=form_data.get("email"),
                    message=form_data.get("message", ""),
                    userinfo_id=user_id,  # Se asigna el ID obtenido de forma segura.
                )
                session.add(db_entry)
                session.commit()
                print("--- FORMULARIO GUARDADO EXITOSAMENTE EN LA BD ---")

        except Exception as e:
            # Si hay un error al guardar, lo veremos en los logs.
            print(f"!!!!!!!!!! ERROR AL GUARDAR EN LA BASE DE DATOS: {e} !!!!!!!!!!!")

        return rx.redirect(navigation.routes.CONTACT_ENTRIES_ROUTE)

    async def list_entries(self):
        """Carga las entradas de contacto SOLO para el usuario autenticado."""
        try:
            self.is_loading = True
            yield
            
            if not self.my_userinfo_id:
                self.entries = []
            else:
                with rx.session() as session:
                    self.entries = session.exec(
                        rx.select(ContactEntryModel).where(ContactEntryModel.userinfo_id == self.my_userinfo_id)
                    ).all()

        except Exception as e:
            print(f"!!!!!!!!!! OCURRIÓ UN ERROR EN list_entries: {e} !!!!!!!!!!!")
        finally:
            self.is_loading = False
            yield