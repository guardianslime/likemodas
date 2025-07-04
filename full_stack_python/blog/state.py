# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo
import asyncio
# La importación de moment se ha eliminado

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE
if BLOG_POSTS_ROUTE.endswith("/"):
    BLOG_POSTS_ROUTE = BLOG_POSTS_ROUTE[:-1]

class BlogPostState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    post_content: str = ""
    post_publish_active: bool = False
    uploaded_image: Optional[str] = None

    # --- ¡NUEVAS VARIABLES! ---
    # Guardaremos la fecha y hora como strings simples para evitar errores
    publish_date_str: str = ""
    publish_time_str: str = ""
    # ---------------------------

    @rx.var
    def image_url(self) -> str:
        if self.post and self.post.image_filename:
            return rx.get_upload_url(self.post.image_filename)
        return ""

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_url(self) -> str:
        if not self.post:
            return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}"

    @rx.var
    def blog_post_edit_url(self) -> str:
        if not self.post:
            return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"

    async def handle_upload(self, files: list[rx.UploadFile]):
        file = files[0]
        data = await file.read()
        path = rx.get_upload_dir() / file.name
        with path.open("wb") as f:
            f.write(data)
        self.uploaded_image = file.name

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None
            return
            
        lookups = (
            (BlogPostModel.userinfo_id == self.my_userinfo_id) &
            (BlogPostModel.id == self.blog_post_id)
        )
        with rx.session() as session:
            if self.blog_post_id == "":
                self.post = None
                return
            
            sql_statement = select(BlogPostModel).options(
                sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
            ).where(lookups)
            result = session.exec(sql_statement).one_or_none()
            
            self.post = result
            if result is None:
                self.post_content = ""
            else:
                self.post_content = self.post.content
                self.post_publish_active = self.post.publish_active

                # --- ¡NUEVA LÓGICA! ---
                # Aquí populamos los strings de fecha y hora
                if self.post.publish_date:
                    self.publish_date_str = self.post.publish_date.strftime("%Y-%m-%d")
                    self.publish_time_str = self.post.publish_date.strftime("%H:%M:%S")
                else:
                    # Si no hay fecha, usamos la actual como default
                    now = datetime.now()
                    self.publish_date_str = now.strftime("%Y-%m-%d")
                    self.publish_time_str = now.strftime("%H:%M:%S")
                # -----------------------

    def load_posts(self, *args, **kwargs):
        # ... este método no cambia
        with rx.session() as session:
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id)
            ).all()
            self.posts = result

    # ... los métodos add_post, save_post_edits y to_blog_post no cambian
    def add_post(self, form_data: dict):
        with rx.session() as session:
            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def save_post_edits(self, post_id: int, updated_data: dict):
        with rx.session() as session:
            post = session.exec(
                select(BlogPostModel).where(
                    BlogPostModel.id == post_id
                )
            ).one_or_none()
            if post is None:
                return
            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            reloaded_post = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(BlogPostModel.id == post_id)
            ).one_or_none()
            self.post = reloaded_post

    def to_blog_post(self, edit_page=False):
        if not self.post:
            return rx.redirect(BLOG_POSTS_ROUTE)
        if edit_page:
            return rx.redirect(f"{self.blog_post_edit_url}")
        return rx.redirect(f"{self.blog_post_url}")


class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}

    def handle_submit(self, form_data):
        data = form_data.copy()
        if self.my_userinfo_id is not None:
            data['userinfo_id'] = self.my_userinfo_id
        if self.uploaded_image:
            data['image_filename'] = self.uploaded_image
        self.form_data = data
        self.add_post(data)
        return self.to_blog_post(edit_page=True)


class BlogEditFormState(BlogPostState):
    form_data: dict = {}

    # --- ¡HEMOS ELIMINADO LOS @rx.var DE AQUÍ! ---

    def handle_submit(self, form_data):
        self.form_data = form_data
        post_id = form_data.pop('post_id')
        publish_date = form_data.pop('publish_date', None)
        publish_time = form_data.pop('publish_time', None)

        final_publish_date = None
        if publish_date and publish_time:
            try:
                publish_input_string = f"{publish_date} {publish_time}"
                final_publish_date = datetime.strptime(publish_input_string, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                final_publish_date = None
        
        publish_active = form_data.pop('publish_active', False) == "on"
        
        updated_data = {**form_data}
        if self.uploaded_image:
            updated_data['image_filename'] = self.uploaded_image
            
        updated_data['publish_active'] = publish_active
        updated_data['publish_date'] = final_publish_date
        self.save_post_edits(post_id, updated_data)
        return self.to_blog_post()