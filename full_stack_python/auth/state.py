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
    publish_date_str: str = ""
    publish_time_str: str = ""
    post_id_str: str = ""

    @rx.var
    def post_images(self) -> list[PostImageModel]:
        if self.post and self.post.images:
            return self.post.images
        return []

    @rx.var
    def preview_image_urls(self) -> list[str]:
        urls = []
        if self.post and self.post.images:
            for img in self.post.images:
                urls.append(f"/_upload/{img.filename}")
        for filename in self.uploaded_images:
            if f"/_upload/{filename}" not in urls:
                urls.append(f"/_upload/{filename}")
        return urls

    # ... (los @rx.var blog_post_id, url y edit_url no cambian) ...

    async def handle_upload(self, files: list[rx.UploadFile]):
        # ... (este método no cambia) ...

    def get_post_detail(self):
        self.uploaded_images = []
        if self.my_userinfo_id is None:
            self.post = None; return
            
        with rx.session() as session:
            if self.blog_post_id == "":
                self.post = None; return
            
            # --- ¡VERIFICACIÓN Y CORRECCIÓN! ---
            # Nos aseguramos de que aquí también se carguen las imágenes.
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(
                    (BlogPostModel.userinfo_id == self.my_userinfo_id) &
                    (BlogPostModel.id == self.blog_post_id)
                )
            ).one_or_none()
            
            self.post = result
            # ... (la lógica de if result/else no cambia) ...

    def load_posts(self, *args, **kwargs):
        with rx.session() as session:
            # --- ¡CORRECCIÓN AQUÍ! ---
            # Cargamos las imágenes también en la lista del blog.
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id)
            ).all()
            self.posts = result

    # ... (el resto de la clase y subclases no cambian) ...