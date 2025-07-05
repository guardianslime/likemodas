# full_stack_python/contact/state.py

from __future__ import annotations
import asyncio
import reflex as rx
from sqlmodel import select
# --- ¡CORRECCIÓN! ---
from typing import Any

from ..auth.state import SessionState
from ..models import ContactEntryModel

class ContactState(SessionState):
    # --- ¡CORRECCIÓN! ---
    # Se especifica el tipo del diccionario para evitar el VarTypeError.
    form_data: dict[str, Any] = {}
    did_submit: bool = False
    entries: list[ContactEntryModel] = []

    @rx.var
    def entries_with_formatted_date(self) -> list[dict]:
        processed_entries = []
        for entry in self.entries:
            entry_dict = entry.dict()
            entry_dict["created_at_formatted"] = entry.created_at.strftime("%Y-%m-%d %H:%M")
            processed_entries.append(entry_dict)
        return processed_entries

    @rx.var
    def thank_you_message(self) -> str:
        first_name = self.form_data.get("first_name", "")
        return f"¡Gracias, {first_name}!" if first_name else "¡Gracias por tu mensaje!"

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

    def load_entries(self):
        with rx.session() as session:
            self.entries = session.exec(
                select(ContactEntryModel).order_by(ContactEntryModel.id.desc())
            ).all()

    def to_post(self):
        if not self.post:
            return rx.redirect(ARTICLE_LIST_ROUTE)
        return rx.redirect(self.post_url)