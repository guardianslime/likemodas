# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List, Any
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel
import os

class BlogPostState(SessionState):
    """Un estado unificado y simple para manejar todo lo relacionado con el blog."""
    
    post: Optional[BlogPostModel] = None
    
    # --- Formulario ---
    post_content: str = ""
    post_publish_active: bool = False
    publish_date_str: str = ""
    publish_time_str: str = ""
    
    # --- Lógica de Imágenes Simple ---
    image_previews: list[str] = []

    @rx.var
    def blog_post_id(self) -> int:
        """Obtiene el ID del blog de la URL como un entero."""
        try:
            return int(self.router.page.params.get("blog_id", 0))
        except:
            return 0
            
    def get_post_detail(self):
        """Al cargar una página de edición, llena el formulario y la galería de vista previa."""
        # Limpiar el estado previo
        self.image_previews = []
        self.post_content = ""
        self.post_publish_active = False
        self.publish_date_str = ""
        self.publish_time_str = ""

        if not self.blog_post_id > 0: 
            self.post = None
            return

        with rx.session() as session:
            self.post = session.exec(
                select(BlogPostModel).options(sqlalchemy.orm.selectinload(BlogPostModel.images))
                .where(BlogPostModel.id == self.blog_post_id)
            ).one_or_none()
        
        if self.post:
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active
            if self.post.publish_date:
                self.publish_date_str = self.post.publish_date.strftime("%Y-%m-%d")
                self.publish_time_str = self.post.publish_date.strftime("%H:%M:%S")
            # Llena la lista de vista previa con las imágenes existentes
            self.image_previews = [f"/_upload/{img.filename}" for img in self.post.images]
        else:
            return rx.redirect("/blog")

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Sube los archivos y los añade a la lista de vista previa."""
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            new_url = f"/_upload/{file.name}"
            if new_url not in self.image_previews:
                self.image_previews.append(new_url)

    def delete_preview_image(self, url: str):
        """Elimina una imagen de la lista de vista previa."""
        self.image_previews.remove(url)
            
    def handle_submit(self, form_data: dict):
        """Manejador unificado para crear y actualizar posts."""
        with rx.session() as session:
            # 1. Obtener o crear el post
            db_post = session.get(BlogPostModel, self.blog_post_id) if self.blog_post_id > 0 else BlogPostModel(userinfo_id=self.my_userinfo_id)
            
            # 2. Actualizar campos
            db_post.title = form_data.get("title")
            db_post.content = self.post_content
            db_post.publish_active = self.post_publish_active
            if self.publish_date_str and self.publish_time_str:
                try: db_post.publish_date = datetime.strptime(f"{self.publish_date_str} {self.publish_time_str}", "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError): db_post.publish_date = None
            else:
                db_post.publish_date = None
            
            session.add(db_post); session.commit(); session.refresh(db_post)
            post_id = db_post.id

            # 3. Sincronizar imágenes
            final_filenames = {os.path.basename(url) for url in self.image_previews}
            existing_images = session.exec(select(PostImageModel).where(PostImageModel.blog_post_id == post_id)).all()
            existing_filenames = {img.filename for img in existing_images}
            
            # Borrar imágenes que ya no están
            for img in existing_images:
                if img.filename not in final_filenames:
                    session.delete(img)
            
            # Añadir imágenes nuevas
            for filename in final_filenames:
                if filename not in existing_filenames:
                    session.add(PostImageModel(filename=filename, blog_post_id=post_id))
            session.commit()
            
        return rx.redirect(f"/blog/{post_id}/edit")