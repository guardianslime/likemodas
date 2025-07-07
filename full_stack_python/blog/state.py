# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
import os

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE
if BLOG_POSTS_ROUTE.endswith("/"):
    BLOG_POSTS_ROUTE = BLOG_POSTS_ROUTE[:-1]

class BlogPostState(SessionState):
    """
    Estado UNIFICADO para manejar todo lo relacionado con los posts:
    listar, ver detalle, editar, y manejar los formularios.
    """
    # --- Variables de la lista y detalle ---
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    
    # --- Variables para el formulario de edición ---
    post_content: str = ""
    post_publish_active: bool = False
    edit_form_data: dict = {}

    # --- Variables para el formulario de añadir ---
    imagenes_temporales: list[str] = []

    # --- Propiedades Calculadas ---
    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_edit_url(self) -> str:
        return f"{BLOG_POSTS_ROUTE}/{self.blog_post_id}/edit"

    @rx.var
    def publish_display_date(self) -> str:
        if self.post and self.post.publish_date:
            return self.post.publish_date.strftime("%Y-%m-%d")
        return datetime.now().strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if self.post and self.post.publish_date:
            return self.post.publish_date.strftime("%H:%M:%S")
        return datetime.now().strftime("%H:%M:%S")

    # --- Lógica de Carga de Datos ---
    def get_post_detail(self):
        if self.my_userinfo_id is None or not self.blog_post_id:
            self.post = None
            return

        with rx.session() as session:
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.images),
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(
                    (BlogPostModel.userinfo_id == self.my_userinfo_id) &
                    (BlogPostModel.id == self.blog_post_id)
                )
            ).one_or_none()
            
            self.post = result
            if self.post:
                self.post_content = self.post.content
                self.post_publish_active = self.post.publish_active
            else:
                self.post_content = ""
                self.post_publish_active = False
    
    def load_posts(self):
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.images))
                .where(BlogPostModel.userinfo_id == self.my_userinfo_id)
                .order_by(BlogPostModel.id.desc())
            ).all()

    # --- Lógica de Formulario de EDICIÓN ---
    def handle_edit_submit(self, form_data: dict):
        self.edit_form_data = form_data
        post_id = form_data.pop('post_id')
        publish_date_str = form_data.pop('publish_date', None)
        publish_time_str = form_data.pop('publish_time', None)
        publish_active = form_data.pop('publish_active', "off") == "on"
        
        final_publish_date = None
        if publish_date_str and publish_time_str:
            try:
                final_publish_date = datetime.strptime(f"{publish_date_str} {publish_time_str}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                final_publish_date = None

        updated_data = {**form_data, 'publish_active': publish_active, 'publish_date': final_publish_date}
        
        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, post_id)
            if post_to_update and post_to_update.userinfo_id == self.my_userinfo_id:
                for key, value in updated_data.items():
                    setattr(post_to_update, key, value)
                session.add(post_to_update)
                session.commit()
                session.refresh(post_to_update)
                self.post = post_to_update

        return rx.redirect(f"{BLOG_POSTS_ROUTE}/{post_id}")

    # --- Lógica de Formulario de AÑADIR ---
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.filename
            with path.open("wb") as f:
                f.write(data)
            if file.filename not in self.imagenes_temporales:
                self.imagenes_temporales.append(file.filename)

    def eliminar_imagen_temp(self, nombre: str):
        if nombre in self.imagenes_temporales:
            self.imagenes_temporales.remove(nombre)
    
    def delete_post(self, post_id: int):
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == self.my_userinfo_id:
                upload_dir = rx.get_upload_dir()
                for image in post_to_delete.images:
                    file_path = upload_dir / image.img_name
                    if file_path.exists():
                        os.remove(file_path)
                session.delete(post_to_delete)
                session.commit()
        self.load_posts()

# La clase para el formulario de añadir se queda separada, pero hereda del estado unificado.
class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        if self.my_userinfo_id is None:
            return rx.window_alert("Error: Debes iniciar sesión para publicar.")
        
        with rx.session() as session:
            post = BlogPostModel(title=form_data.get("title", "Sin Título"), content=form_data.get("content", ""), userinfo_id=self.my_userinfo_id)
            session.add(post)
            session.commit()
            session.refresh(post)
            for img_name in self.imagenes_temporales:
                image_entry = PostImageModel(img_name=img_name, post_id=post.id)
                session.add(image_entry)
            session.commit()
            self.post = post
        self.imagenes_temporales = []
        return rx.redirect(BLOG_POSTS_ROUTE)

# Clase para el blog público, esta se mantiene igual.
class BlogPublicState(SessionState):
    # ... (código sin cambios)
    pass