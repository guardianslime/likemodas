from __future__ import annotations
import asyncio
import reflex as rx
from sqlmodel import select

from ..auth.state import SessionState
from ..models import ContactEntryModel

class ContactState(SessionState):
    form_data: dict = {}
    did_submit: bool = False
    entries: list[ContactEntryModel] = []

    @rx.var
    def thank_you_message(self) -> str:
        first_name = self.form_data.get("first_name", "")
        return f"¡Gracias, {first_name}!" if first_name else "¡Gracias por tu mensaje!"

    search_query: str = ""

    # --- 👇 AÑADIR ESTA PROPIEDAD COMPUTADA 👇 ---
    @rx.var
    def filtered_entries(self) -> list[ContactEntryModel]:
        """Filtra las entradas de contacto por nombre, email o mensaje."""
        if not self.search_query.strip():
            return self.entries
            
        query = self.search_query.lower()
        results = []
        for entry in self.entries:
            # Construimos un texto de búsqueda con los datos relevantes
            search_text = f"{entry.first_name} {entry.last_name} {entry.email} {entry.message}".lower()
            if query in search_text:
                results.append(entry)
        return results

    async def handle_submit(self, form_data: dict):
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
        with rx.session() as session:
            self.entries = session.exec(
                select(ContactEntryModel).order_by(ContactEntryModel.id.desc())
            ).all()
