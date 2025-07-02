# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List, Any
import reflex as rx
import sqlalchemy
from sqlmodel import select
import os 
from rxconfig import config # 1. Importa la configuración de tu app

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
    uploaded_image_url: str = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        """
        Maneja la subida del archivo de imagen.
        """
        if not files:
            return
        
        file = files[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        
        upload_dir = ".web/public"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        
        upload_data = await file.read()
        with open(file_path, "wb") as f:
            f.write(upload_data)
        
        # --- INICIO DE LA CORRECCIÓN ---
        # 2. Obtenemos la URL del backend directamente desde la configuración.
        #    Se convierte a string para asegurar compatibilidad.
        api_url = str(config.api_url)
        
        # 3. Creamos la URL completa de la imagen.
        self.uploaded_image_url = f"{api_url}/{filename}"
        # --- FIN DE LA CORRECIÓN ---


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

    @rx.var
    def post_publish_date_formatted(self) -> str:
        if self.post and self.post.publish_date:
            return self.post.publish_date.strftime("%Y-%m-%d %H:%M")
        return ""

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None; self.post_content = ""; self.post_publish_active = False; return
        try:
            post_id_num = int(self.blog_post_id)
        except (ValueError, TypeError):
            self.post = None; return
        lookups = ((BlogPostModel.userinfo_id == self.my_userinfo_id) & (BlogPostModel.id == post_id_num))
        with rx.session() as session:
            result = session.exec(select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)).where(lookups)).one_or_none()
            self.post = result
            if result is None: self.post_content = ""; return
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active

    def load_posts(self, *args, **kwargs):
        with rx.session() as session:
            self.posts = session.exec(select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo)).where(BlogPostModel.userinfo_id == self.my_userinfo_id)).all()

    def add_post(self, form_data: dict):
        with rx.session() as session:
            if self.uploaded_image_url:
                form_data['image_url'] = self.uploaded_image_url
            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post
            self.uploaded_image_url = ""

    def save_post_edits(self, post_id: int, updated_data: dict):
        with rx.session() as session:
            post = session.exec(select(BlogPostModel).where(BlogPostModel.id == post_id)).one_or_none()
            if post is None: return
            if self.uploaded_image_url:
                updated_data['image_url'] = self.uploaded_image_url
            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            self.uploaded_image_url = ""
            session.refresh(post)
            self.post = post

    def to_blog_post(self, edit_page=False):
        if not self.post: return rx.redirect(BLOG_POSTS_ROUTE)
        return rx.redirect(f"{self.blog_post_edit_url}") if edit_page else rx.redirect(f"{self.blog_post_url}")

class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}
    def handle_submit(self, form_data: dict):
        data = form_data.copy()
        if self.my_userinfo_id is not None: data['userinfo_id'] = self.my_userinfo_id
        self.add_post(data)
        return self.to_blog_post(edit_page=True)

class BlogEditFormState(BlogPostState):
    form_data: dict = {}
    @rx.var
    def publish_display_date(self) -> str:
        if not self.post or not self.post.publish_date: return datetime.now().strftime("%Y-%m-%d")
        return self.post.publish_date.strftime("%Y-%m-%d")
    @rx.var
    def publish_display_time(self) -> str:
        if not self.post or not self.post.publish_date: return datetime.now().strftime("%H:%M:%S")
        return self.post.publish_date.strftime("%H:%M:%S")
    def handle_submit(self, form_data: dict):
        post_id = form_data.pop('post_id'); publish_date_str = form_data.pop('publish_date', None)
        publish_time_str = form_data.pop('publish_time', None)
        try: final_publish_date = datetime.strptime(f"{publish_date_str} {publish_time_str}", "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError): final_publish_date = None
        form_data['publish_active'] = form_data.get('publish_active') == "on"; form_data['publish_date'] = final_publish_date
        self.save_post_edits(post_id, form_data)
        return self.to_blog_post()
