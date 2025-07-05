# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select, Session
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel
import asyncio
import os

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE
if BLOG_POSTS_ROUTE.endswith("/"):
    BLOG_POSTS_ROUTE = BLOG_POSTS_ROUTE[:-1]

class BlogPostState(SessionState):
    """Un estado unificado y simple para manejar todo lo relacionado con el blog."""
    
    post: Optional[BlogPostModel] = None
    
    # --- Fuentes de datos para el formulario ---
    post_content: str = ""
    post_publish_active: bool = False
    publish_date_str: str = ""
    publish_time_str: str = ""
    
    # --- LA NUEVA LÓGICA SIMPLE PARA IMÁGENES ---
    # Una única lista que controla la vista previa.
    image_urls: list[str] = []

    @rx.var
    def blog_post_id(self) -> int:
        """Obtiene el ID del blog como un entero."""
        try:
            return int(self.router.page.params.get("blog_id", 0))
        except:
            return 0

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de archivos y los añade a la lista de vista previa."""
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            
            # Construye la URL y la añade a la lista de vista previa
            new_url = f"/_upload/{file.name}"
            if new_url not in self.image_urls:
                self.image_urls.append(new_url)

    def delete_image(self, url: str):
        """Elimina una imagen de la lista de vista previa."""
        self.image_urls.remove(url)

    def get_post_detail(self):
        """Carga los datos de un post existente para editarlo."""
        if not self.blog_post_id: return

        with rx.session() as session:
            self.post = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(BlogPostModel.id == self.blog_post_id)
            ).one_or_none()
        
        if self.post:
            # Popula el formulario con los datos del post
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active
            if self.post.publish_date:
                self.publish_date_str = self.post.publish_date.strftime("%Y-%m-%d")
                self.publish_time_str = self.post.publish_date.strftime("%H:%M:%S")
            
            # --- Llena la lista de vista previa con las imágenes existentes ---
            self.image_urls = [f"/_upload/{img.filename}" for img in self.post.images]
        else:
            # Si el post no se encuentra, redirige
            return rx.redirect(BLOG_POSTS_ROUTE)
            
    def handle_submit(self, form_data: dict):
        """Un único manejador para crear o actualizar un post."""
        post_id = self.blog_post_id if self.blog_post_id > 0 else None
        
        with rx.session() as session:
            # Determina si es un post nuevo o existente
            if post_id:
                # Actualizar un post existente
                db_post = session.get(BlogPostModel, post_id)
            else:
                # Crear un post nuevo
                db_post = BlogPostModel(userinfo_id=self.my_userinfo_id)
            
            # Actualiza los campos del post
            db_post.title = form_data.get("title")
            db_post.content = self.post_content
            db_post.publish_active = self.post_publish_active
            
            if self.publish_date_str and self.publish_time_str:
                try:
                    db_post.publish_date = datetime.strptime(f"{self.publish_date_str} {self.publish_time_str}", "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    db_post.publish_date = None
            else:
                db_post.publish_date = None

            session.add(db_post)
            session.commit()
            session.refresh(db_post)
            post_id = db_post.id # Aseguramos tener el ID

            # --- Lógica de sincronización de imágenes ---
            # Obtiene los nombres de archivo de la lista de vista previa
            final_filenames = {os.path.basename(url) for url in self.image_urls}
            
            # Obtiene los nombres de archivo actuales de la base de datos
            existing_images = session.exec(select(PostImageModel).where(PostImageModel.blog_post_id == post_id)).all()
            existing_filenames = {img.filename for img in existing_images}
            
            # Borra las imágenes que ya no están en la lista de vista previa
            for img in existing_images:
                if img.filename not in final_filenames:
                    session.delete(img)
            
            # Añade las imágenes nuevas que no están en la base de datos
            for filename in final_filenames:
                if filename not in existing_filenames:
                    session.add(PostImageModel(filename=filename, blog_post_id=post_id))

            session.commit()

        # Redirige a la página de edición del post recién guardado
        return rx.redirect(f"/blog/{post_id}/edit")