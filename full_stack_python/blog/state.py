# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel
import asyncio

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE
if BLOG_POSTS_ROUTE.endswith("/"):
    BLOG_POSTS_ROUTE = BLOG_POSTS_ROUTE[:-1]

class BlogPostState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    post_content: str = ""
    post_publish_active: bool = False
    uploaded_images: list[str] = []
    
    # Variables para los inputs controlados del formulario
    publish_date_str: str = ""
    publish_time_str: str = ""
    post_id_str: str = "" # Variable segura para el ID del post

    @rx.var
    def post_images(self) -> list[PostImageModel]:
        """Devuelve de forma segura la lista de imágenes del post, o una lista vacía."""
        if self.post and self.post.images:
            return self.post.images
        return []

    @rx.var
    def preview_image_urls(self) -> list[str]:
        """Combina imágenes existentes y nuevas para la vista previa en el formulario de edición."""
        urls = []
        if self.post and self.post.images:
            for img in self.post.images:
                urls.append(f"/_upload/{img.filename}")
        for filename in self.uploaded_images:
            if f"/_upload/{filename}" not in urls:
                urls.append(f"/_upload/{filename}")
        return urls

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_url(self) -> str:
        if not self.post: return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}"

    @rx.var
    def blog_post_edit_url(self) -> str:
        if not self.post: return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f: f.write(data)
            if file.name not in self.uploaded_images:
                self.uploaded_images.append(file.name)

    def get_post_detail(self):
        self.uploaded_images = []
        if self.my_userinfo_id is None:
            self.post = None; return
        
        with rx.session() as session:
            if self.blog_post_id == "":
                self.post = None; return
            
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.selectinload(BlogPostModel.images) # Carga ansiosa de imágenes
                ).where(
                    (BlogPostModel.userinfo_id == self.my_userinfo_id) &
                    (BlogPostModel.id == self.blog_post_id)
                )
            ).one_or_none()
            self.post = result
            
            if result:
                self.post_content = self.post.content
                self.post_publish_active = self.post.publish_active
                self.post_id_str = str(self.post.id)
                if self.post.publish_date:
                    self.publish_date_str = self.post.publish_date.strftime("%Y-%m-%d")
                    self.publish_time_str = self.post.publish_date.strftime("%H:%M:%S")
                else:
                    now = datetime.now()
                    self.publish_date_str = now.strftime("%Y-%m-%d")
                    self.publish_time_str = now.strftime("%H:%M:%S")
            else:
                self.post_content = ""; self.post_id_str = ""

    def load_posts(self, *args, **kwargs):
        with rx.session() as session:
            # --- CORRECCIÓN: Añadido selectinload para cargar imágenes en la lista ---
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo),
                    sqlalchemy.orm.selectinload(BlogPostModel.images) 
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id)
            ).all()
            self.posts = result

    def add_post_and_images(self, form_data: dict, image_filenames: list[str]):
        with rx.session() as session:
            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit(); session.refresh(post)
            for filename in image_filenames:
                session.add(PostImageModel(filename=filename, blog_post_id=post.id))
            session.commit(); session.refresh(post)
            self.post = post

    def add_images_to_post(self, post_id: int, image_filenames: list[str]):
        with rx.session() as session:
            for filename in image_filenames:
                session.add(PostImageModel(filename=filename, blog_post_id=post_id))
            session.commit()
        self.get_post_detail()

    def to_blog_post(self, edit_page=False):
        if not self.post: return rx.redirect(BLOG_POSTS_ROUTE)
        if edit_page: return rx.redirect(self.blog_post_edit_url)
        return rx.redirect(self.blog_post_url)


class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}
    def handle_submit(self, form_data):
        data = form_data.copy()
        if self.my_userinfo_id is not None:
            data['userinfo_id'] = self.my_userinfo_id
        self.add_post_and_images(data, self.uploaded_images)
        return self.to_blog_post(edit_page=True)

class BlogEditFormState(BlogPostState):
    form_data: dict = {}
    def handle_submit(self, form_data):
        post_id = int(form_data.pop('post_id'))
        if self.uploaded_images:
            self.add_images_to_post(post_id, self.uploaded_images)
        publish_date = form_data.pop('publish_date', None)
        publish_time = form_data.pop('publish_time', None)
        final_publish_date = None
        if publish_date and publish_time:
            try:
                final_publish_date = datetime.strptime(f"{publish_date} {publish_time}", "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError): pass
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post:
                post.title = form_data.get("title", post.title)
                post.content = form_data.get("content", post.content)
                post.publish_active = form_data.pop('publish_active', False) == "on"
                post.publish_date = final_publish_date
                session.add(post)
                session.commit()
        return self.to_blog_post()