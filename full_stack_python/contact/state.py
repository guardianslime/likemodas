# full_stack_python/contact/state.py

from __future__ import annotations
import asyncio
import reflex as rx

from .. import navigation  # ¡NUEVO! Importamos navigation para usar las rutas.
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
        Evento para asegurar que la sesión del usuario esté cargada 
        antes de ejecutar otras lógicas.
        """
        # No se necesita código aquí, su ejecución en la cadena de on_load es suficiente.
        yield

    async def handle_submit(self, form_data: dict):
        """Maneja el envío del formulario."""
        self.form_data = form_data
        
        # --- IMPRESIÓN PARA DEPURACIÓN ---
        # Este mensaje aparecerá en tu terminal del servidor.
        print(f"--- FORMULARIO DE CONTACTO RECIBIDO ---")
        print(f"Datos: {form_data}")
        # -----------------------------------------
        
        with rx.session() as session:
            user_info = self.authenticated_user_info
            
            # --- IMPRESIÓN PARA DEPURACIÓN ---
            if user_info:
                print(f"Usuario autenticado encontrado: ID {user_info.id}")
            else:
                print("No se encontró un usuario autenticado para asociar.")
            # -----------------------------------------

            db_entry = ContactEntryModel(
                first_name=form_data.get("first_name", ""),
                last_name=form_data.get("last_name"),
                email=form_data.get("email"),
                message=form_data.get("message", ""),
                userinfo_id=user_info.id if user_info else None,
            )
            session.add(db_entry)
            session.commit()

        # ARREGLO: Redirige al usuario a la lista de entradas después de enviar.
        return rx.redirect(navigation.routes.CONTACT_ENTRIES_ROUTE)

    async def list_entries(self):
        """Carga las entradas de contacto SOLO para el usuario autenticado."""
        try:
            self.is_loading = True
            yield

            user_info = self.authenticated_user_info
            # Si no hay un usuario logueado, la lista de entradas queda vacía.
            if not user_info:
                self.entries = []
            else:
                # Si hay un usuario, se buscan solo sus entradas.
                with rx.session() as session:
                    self.entries = session.exec(
                        rx.select(ContactEntryModel).where(ContactEntryModel.userinfo_id == user_info.id)
                    ).all()
                    
                    # --- IMPRESIÓN PARA DEPURACIÓN ---
                    print(f"--- CARGANDO ENTRADAS PARA USUARIO ID {user_info.id} ---")
                    print(f"Se encontraron {len(self.entries)} entradas.")
                    # -----------------------------------------

        except Exception as e:
            print(f"!!!!!!!!!! OCURRIÓ UN ERROR EN list_entries: {e} !!!!!!!!!!!")
        finally:
            self.is_loading = False
            yield