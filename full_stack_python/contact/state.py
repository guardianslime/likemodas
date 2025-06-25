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

    # ¡FUNCIÓN DE DIAGNÓSTICO!
    async def list_entries(self):
        """Carga las entradas de contacto con logs para depuración."""
        print("--- DEBUG: El evento list_entries ha COMENZADO. ---")
        try:
            self.is_loading = True
            yield
            print("--- DEBUG: is_loading se ha establecido en True. ---")

            print("--- DEBUG: Intentando abrir la sesión con la base de datos... ---")
            with rx.session() as session:
                print("--- DEBUG: Sesión con la base de datos ABIERTA. Ejecutando la consulta... ---")
                self.entries = session.exec(
                    rx.select(ContactEntryModel)
                ).all()
                print(f"--- DEBUG: Consulta EJECUTADA. Se encontraron {len(self.entries)} entradas. ---")

        except Exception as e:
            print(f"!!!!!!!!!! DEBUG: OCURRIÓ UN ERROR: {e} !!!!!!!!!!!")
        finally:
            print("--- DEBUG: Bloque FINALLY alcanzado. Estableciendo is_loading en False. ---")
            self.is_loading = False
            yield
            print("--- DEBUG: El evento list_entries ha FINALIZADO. ---")