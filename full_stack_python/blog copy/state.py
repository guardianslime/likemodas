from datetime import datetime
from typing import Optional, List
import reflex as rx

import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import ContactPostModel, UserInfo

CONTACT_POSTS_ROUTE = navigation.routes.CONTACT_POSTS_ROUTE
if CONTACT_POSTS_ROUTE.endswith("/"):
    CONTACT_POSTS_ROUTE = CONTACT_POSTS_ROUTE[:-1]

class ContactPostState(SessionState):
    posts: List["ContactPostModel"] = []
    post: Optional["ContactPostModel"] = None
    post_content: str = ""
    post_publish_active: bool = False

    @rx.var
    def contact_post_id(self) -> str:  # Añadida la anotación de tipo -> str
        return self.router.page.params.get("contact_id", "")

    @rx.var
    def contact_post_url(self) -> str: # Añadida la anotación de tipo -> str
        if not self.post:
            return f"{CONTACT_POSTS_ROUTE}"
        return f"{CONTACT_POSTS_ROUTE}/{self.post.id}"

    @rx.var
    def contact_post_edit_url(self) -> str: # Añadida la anotación de tipo -> str
        if not self.post:
            return f"{CONTACT_POSTS_ROUTE}"
        return f"{CONTACT_POSTS_ROUTE}/{self.post.id}/edit"

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None
            self.post_content = ""
            self.post_publish_active = False
            return
        lookups = (
            (ContactPostModel.userinfo_id == self.my_userinfo_id) &
            (ContactPostModel.id == self.contact_post_id)
        )
        with rx.session() as session:
            if self.contact_post_id == "":
                self.post = None
                return
            sql_statement = select(ContactPostModel).options(
                sqlalchemy.orm.joinedload(ContactPostModel.userinfo).joinedload(UserInfo.user)
            ).where(lookups)
            result = session.exec(sql_statement).one_or_none()
            # if result.userinfo: # db lookup
            #     print('working')
            #     result.userinfo.user
            self.post = result
            if result is None:
                self.post_content = ""
                return
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active

    def load_posts(self, *args, **kwargs):
        # if published_only:
        #     lookup_args = (
        #         (ContactPostModel.publish_active == True) &
        #         (ContactPostModel.publish_date < datetime.now())
        #     )
        with rx.session() as session:
            result = session.exec(
                select(ContactPostModel).options(
                    sqlalchemy.orm.joinedload(ContactPostModel.userinfo)
                ).where(ContactPostModel.userinfo_id == self.my_userinfo_id)
            ).all()
            self.posts = result

    def add_post(self, form_data: dict):
        with rx.session() as session:
            post = ContactPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def save_post_edits(self, post_id: int, updated_data: dict):
        with rx.session() as session:
            post = session.exec(
                select(ContactPostModel).where(
                    ContactPostModel.id == post_id
                )
            ).one_or_none()
            if post is None:
                return
            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def to_contact_post(self, edit_page=False):
        if not self.post:
            return rx.redirect(CONTACT_POSTS_ROUTE)
        if edit_page:
            return rx.redirect(f"{self.contact_post_edit_url}")
        return rx.redirect(f"{self.contact_post_url}")


class ContactAddPostFormState(ContactPostState):
    form_data: dict = {}

    def handle_submit(self, form_data):
        data = form_data.copy()
        if self.my_userinfo_id is not None:
            data['userinfo_id'] = self.my_userinfo_id
        self.form_data = data
        self.add_post(data)
        return self.to_contact_post(edit_page=True)


class ContactEditFormState(ContactPostState):
    form_data: dict = {}

    @rx.var
    def publish_display_date(self) -> str:
        if not self.post:
            return datetime.now().strftime("%Y-%m-%d")
        if not self.post.publish_date:
            return datetime.now().strftime("%Y-%m-%d")
        return self.post.publish_date.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if not self.post:
            return datetime.now().strftime("%H:%M:%S")
        if not self.post.publish_date:
            return datetime.now().strftime("%H:%M:%S")
        return self.post.publish_date.strftime("%H:%M:%S")

    def handle_submit(self, form_data):
        self.form_data = form_data
        post_id = form_data.pop('post_id')
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
        self.save_post_edits(post_id, updated_data)
        return self.to_contact_post()