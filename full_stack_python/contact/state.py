from datetime import datetime
from typing import Optional, List
import reflex as rx

import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import ContactEntryModel, UserInfo

CONTACT_POSTS_ROUTE = navigation.routes.CONTACT_POSTS_ROUTE
if CONTACT_POSTS_ROUTE.endswith("/"):
    CONTACT_POSTS_ROUTE = CONTACT_POSTS_ROUTE[:-1]

class ContactEntryState(SessionState):
    entrys: List["ContactEntryModel"] = []
    entry: Optional["ContactEntryModel"] = None
    entry_content: str = ""
    entry_publish_active: bool = False

    @rx.var
    def contact_entry_id(self) -> str:  # Añadida la anotación de tipo -> str
        return self.router.page.params.get("contact_id", "")

    @rx.var
    def contact_entry_url(self) -> str: # Añadida la anotación de tipo -> str
        if not self.entry:
            return f"{CONTACT_POSTS_ROUTE}"
        return f"{CONTACT_POSTS_ROUTE}/{self.entry.id}"

    @rx.var
    def contact_entry_edit_url(self) -> str: # Añadida la anotación de tipo -> str
        if not self.entry:
            return f"{CONTACT_POSTS_ROUTE}"
        return f"{CONTACT_POSTS_ROUTE}/{self.entry.id}/edit"

    def get_entry_detail(self):
        if self.my_userinfo_id is None:
            self.entry = None
            self.entry_content = ""
            self.entry_publish_active = False
            return
        lookups = (
            (ContactEntryModel.userinfo_id == self.my_userinfo_id) &
            (ContactEntryModel.id == self.contact_entry_id)
        )
        with rx.session() as session:
            if self.contact_entry_id == "":
                self.entry = None
                return
            sql_statement = select(ContactEntryModel).options(
                sqlalchemy.orm.joinedload(ContactEntryModel.userinfo).joinedload(UserInfo.user)
            ).where(lookups)
            result = session.exec(sql_statement).one_or_none()
            # if result.userinfo: # db lookup
            #     print('working')
            #     result.userinfo.user
            self.entry = result
            if result is None:
                self.entry_content = ""
                return
            self.entry_content = self.entry.content
            self.entry_publish_active = self.entry.publish_active

    def load_entrys(self, *args, **kwargs):
        # if published_only:
        #     lookup_args = (
        #         (ContactEntryModel.publish_active == True) &
        #         (ContactEntryModel.publish_date < datetime.now())
        #     )
        with rx.session() as session:
            result = session.exec(
                select(ContactEntryModel).options(
                    sqlalchemy.orm.joinedload(ContactEntryModel.userinfo)
                ).where(ContactEntryModel.userinfo_id == self.my_userinfo_id)
            ).all()
            self.entrys = result

    def add_entry(self, form_data: dict):
        with rx.session() as session:
            entry = ContactEntryModel(**form_data)
            session.add(entry)
            session.commit()
            session.refresh(entry)
            self.entry = entry

    def save_entry_edits(self, entry_id: int, updated_data: dict):
        with rx.session() as session:
            entry = session.exec(
                select(ContactEntryModel).where(
                    ContactEntryModel.id == entry_id
                )
            ).one_or_none()
            if entry is None:
                return
            for key, value in updated_data.items():
                setattr(entry, key, value)
            session.add(entry)
            session.commit()
            session.refresh(entry)
            self.entry = entry

    def to_contact_entry(self, edit_page=False):
        if not self.entry:
            return rx.redirect(CONTACT_POSTS_ROUTE)
        if edit_page:
            return rx.redirect(f"{self.contact_entry_edit_url}")
        return rx.redirect(f"{self.contact_entry_url}")


class ContactAddEntryFormState(ContactEntryState):
    form_data: dict = {}

    def handle_submit(self, form_data):
        data = form_data.copy()
        if self.my_userinfo_id is not None:
            data['userinfo_id'] = self.my_userinfo_id
        self.form_data = data
        self.add_entry(data)
        return self.to_contact_entry(edit_page=True)


class ContactEditFormState(ContactEntryState):
    form_data: dict = {}

    @rx.var
    def publish_display_date(self) -> str:
        if not self.entry:
            return datetime.now().strftime("%Y-%m-%d")
        if not self.entry.publish_date:
            return datetime.now().strftime("%Y-%m-%d")
        return self.entry.publish_date.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if not self.entry:
            return datetime.now().strftime("%H:%M:%S")
        if not self.entry.publish_date:
            return datetime.now().strftime("%H:%M:%S")
        return self.entry.publish_date.strftime("%H:%M:%S")

    def handle_submit(self, form_data):
        self.form_data = form_data
        entry_id = form_data.pop('entry_id')
        publish_date = None
        if 'publish_date' in form_data:
            publish_date = form_data.pop('publish_date')
        publish_time = None
        if 'publish_time' in form_data:
            publish_time = form_data.pop('publish_time')
        publish_input_string = f"{publish_date} {publish_time}"
        try:
            final_publish_date = datetime.strptime(publish_input_string, "%Y-%m-%d %H:%M:%S")
        except:
            final_publish_date = None
        publish_active = False
        if 'publish_active' in form_data:
            publish_active = form_data.pop('publish_active') == "on"
        updated_data = {**form_data}
        updated_data['publish_active'] = publish_active
        updated_data['publish_date'] = final_publish_date
        self.save_entry_edits(entry_id, updated_data)
        return self.to_contact_entry()