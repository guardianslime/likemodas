# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List, Any
import reflex as rx
import sqlalchemy
from sqlmodel import select
import os

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel

class BlogPostState(SessionState):
    """Un estado unificado y simple para manejar todo lo relacionado con el blog."""
    
    # El post actual que se está creando o editando
    post: Optional[BlogPostModel] = None
    
    # La lista de todos los posts del usuario (para la página /blog)
    posts: List[BlogPostModel] = []
    
    # Variables del formulario
    post_content: str = ""
    post_publish_active: bool = False
    publish_date_str: str = ""
    publish_time_str: str = ""
    
    # La ÚNICA fuente de verdad para la galería de vista previa, como en tu referencia.
    image_previews: list[str] = []

    @rx.var
    def blog_post_id(self) -> int:
        try:
            return int(self.router.page.params.get("blog_id", 0))
        except:
            return 0
            
    def get_post_detail(self):
        """
        Este evento se llama al montar la página de edición.
        Limpia el estado y carga los datos del post si existe un ID.
        """
        # Reinicia el estado para una carga limpia
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
            self.image_previews = [f"/_upload/{img.filename}" for img in self.post.images]
        else:
            return rx.redirect("/blog")

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Sube archivos y los añade a la lista de vista previa, como en tu referencia."""
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
            post_id = self.blog_post_id if self.blog_post_id > 0 else None
            db_post = session.get(BlogPostModel, post_id) if post_id else BlogPostModel(userinfo_id=self.my_userinfo_id)
            
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

            final_filenames = {os.path.basename(url) for url in self.image_previews}
            existing_images = session.exec(select(PostImageModel).where(PostImageModel.blog_post_id == post_id)).all()
            existing_filenames = {img.filename for img in existing_images}
            
            for img in existing_images:
                if img.filename not in final_filenames:
                    session.delete(img)
            
            for filename in final_filenames:
                if filename not in existing_filenames:
                    session.add(PostImageModel(filename=filename, blog_post_id=post_id))
            session.commit()
            
        return rx.redirect(f"/blog/{post_id}/edit")

    def load_posts(self):
        """Carga la lista de posts del usuario para la página /blog."""
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(sqlalchemy.orm.selectinload(BlogPostModel.images))
                .where(BlogPostModel.userinfo_id == self.my_userinfo_id).order_by(BlogPostModel.id.desc())
            ).all()