from datetime import datetime
from typing import Optional, List
import typing
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE
if BLOG_POSTS_ROUTE.endswith("/"):
    BLOG_POSTS_ROUTE = BLOG_POSTS_ROUTE[:-1]

class BlogPostState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    post_content: str = ""
    post_publish_active: bool = False
    img: list[str] = []

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

    async def handle_upload(self, files: typing.Any):
        """
        Maneja la información de los archivos para la v0.5.0.
        El archivo que llega es un diccionario.
        """
        for file in files:
            filename = file.get("filename")
            if filename:
                self.img.append(f"/{filename}")
        return

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None
            self.post_content = ""
            self.post_publish_active = False
            return
        lookups = (
            (BlogPostModel.userinfo_id == self.my_userinfo_id) &
            (BlogPostModel.id == self.blog_post_id)
        )
        with rx.session() as session:
            if self.blog_post_id == "":
                self.post = None
                return
            result = session.exec(select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)).where(lookups)).one_or_none()
            self.post = result
            if result is None:
                self.post_content = ""
                return
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active

    def load_posts(self, *args, **kwargs):
        with rx.session() as session:
            self.posts = session.exec(select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo)).where(BlogPostModel.userinfo_id == self.my_userinfo_id)).all()

    def add_post(self, form_data: dict):
        with rx.session() as session:
            if self.img:
                form_data['image_url'] = self.img[0]
            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post
            self.img = []

    def save_post_edits(self, post_id: int, updated_data: dict):
        with rx.session() as session:
            post = session.exec(select(BlogPostModel).where(BlogPostModel.id == post_id)).one_or_none()
            if post is None: return
            if self.img:
                updated_data['image_url'] = self.img[0]
            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            self.img = []
            self.post = session.exec(select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)).where(BlogPostModel.id == post_id)).one_or_none()

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
        self.form_data = data
        self.add_post(data)
        return self.to_blog_post(edit_page=True)

class BlogEditFormState(BlogPostState):
    form_data: dict = {}

    @rx.var
    def publish_display_date(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%Y-%m-%d")
        return self.post.publish_date.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%H:%M:%S")
        return self.post.publish_date.strftime("%H:%M:%S")

    def handle_submit(self, form_data):
        post_id = form_data.pop('post_id')
        publish_date_str = form_data.pop('publish_date', None)
        publish_time_str = form_data.pop('publish_time', None)
        try:
            final_publish_date = datetime.strptime(f"{publish_date_str} {publish_time_str}", "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            final_publish_date = None
        form_data['publish_active'] = form_data.get('publish_active') == "on"
        form_data['publish_date'] = final_publish_date
        self.save_post_edits(post_id, form_data)
        return self.to_blog_post()