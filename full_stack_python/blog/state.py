# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel # Importar PostImageModel
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
    image_preview_url: str = ""

    # --- NUEVO: Variable simple para el ID del post ---
    post_id_str: str = ""

    # ... (El resto de los @rx.var no cambian) ...
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
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            if file.name not in self.uploaded_images:
                self.uploaded_images.append(file.name)

    def get_post_detail(self):
        self.uploaded_images = []
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
                sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user),
                sqlalchemy.orm.selectinload(BlogPostModel.images)
            ).where(lookups)
            result = session.exec(sql_statement).one_or_none()
            
            self.post = result
            if result is None:
                self.post_content = ""
                self.image_preview_url = ""
                self.post_id_str = "" # Limpiar ID
            else:
                self.post_content = self.post.content
                self.post_publish_active = self.post.publish_active
                
                # --- NUEVO: Asignamos el ID a nuestra variable segura ---
                self.post_id_str = str(self.post.id)
                
                if self.post.image_filename:
                    self.image_preview_url = f"/_upload/{self.post.image_filename}"
                else:
                    self.image_preview_url = ""

                if self.post.publish_date:
                    self.publish_date_str = self.post.publish_date.strftime("%Y-%m-%d")
                    self.publish_time_str = self.post.publish_date.strftime("%H:%M:%S")
                else:
                    now = datetime.now()
                    self.publish_date_str = now.strftime("%Y-%m-%d")
                    self.publish_time_str = now.strftime("%H:%M:%S")
    # ... (load_posts y to_blog_post no cambian) ...

    def add_post_and_images(self, form_data: dict, image_filenames: list[str]):
        """Añade un post y luego sus imágenes."""
        with rx.session() as session:
            # Crear el post principal
            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)

            # Crear y asociar las imágenes
            for filename in image_filenames:
                image_entry = PostImageModel(filename=filename, blog_post_id=post.id)
                session.add(image_entry)
            
            session.commit()
            session.refresh(post) # Refrescar de nuevo para cargar las imágenes
            self.post = post

    def add_images_to_post(self, post_id: int, image_filenames: list[str]):
        """Añade nuevas imágenes a un post existente."""
        with rx.session() as session:
            for filename in image_filenames:
                image_entry = PostImageModel(filename=filename, blog_post_id=post_id)
                session.add(image_entry)
            session.commit()
        # Recargar el post para que la UI se actualice
        self.get_post_detail()

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
        post_id_str = form_data.pop('post_id')
        post_id = int(post_id_str)

        if self.uploaded_images:
            self.add_images_to_post(post_id, self.uploaded_images)
        
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
        
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post:
                post.title = form_data.get("title", post.title)
                post.content = form_data.get("content", post.content)
                post.publish_active = publish_active
                post.publish_date = final_publish_date
                session.add(post)
                session.commit()
        
        return self.to_blog_post()