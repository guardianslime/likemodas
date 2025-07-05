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
    def preview_image_urls(self) -> list[str]:
        """Combina imágenes existentes y nuevas para la vista previa en el formulario de edición."""
        urls = []
        if self.post and self.post.images:
            for img in self.post.images:
                urls.append(f"/_upload/{img.filename}")
        for filename in self.uploaded_images:
            # Previene duplicados en la vista previa si una imagen se sube dos veces
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

    def load_posts(self):
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id).order_by(BlogPostModel.id.desc())
            ).all()

    def get_post_detail(self):
        """Carga los detalles de un post para las páginas de detalle y edición."""
        self.uploaded_images = [] # Limpiar imágenes nuevas al cargar la página
        if not self.my_userinfo_id or not self.blog_post_id:
            self.post = None; return
        
        self.post = self._load_post_by_id(int(self.blog_post_id))
        
        if self.post:
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
        """Carga la lista de posts del usuario."""
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id).order_by(BlogPostModel.id.desc())
            ).all()

    def to_blog_post(self, edit_page=False):
        """Redirige a la página del post actual."""
        if not self.post: return rx.redirect(BLOG_POSTS_ROUTE)
        if edit_page: return rx.redirect(self.blog_post_edit_url)
        return rx.redirect(self.blog_post_url)


class BlogAddPostFormState(BlogPostState):
    """Maneja la lógica para el formulario de añadir post."""
    def handle_submit(self, form_data: dict):
        with rx.session() as session:
            # Prepara los datos del post
            post_data = form_data.copy()
            post_data['userinfo_id'] = self.my_userinfo_id
            
            # Crea el objeto del post
            post_obj = BlogPostModel(**post_data)
            session.add(post_obj)
            session.commit()
            session.refresh(post_obj)
            post_id = post_obj.id # Obtenemos el ID del nuevo post

            # Añade las imágenes asociadas al nuevo post
            for filename in self.uploaded_images:
                session.add(PostImageModel(filename=filename, blog_post_id=post_id))
            session.commit()
        
        # Recargamos el post recién creado para tener toda la info en el estado
        self.post = self._load_post_by_id(post_id)
        return self.to_blog_post(edit_page=True)


class BlogEditFormState(BlogPostState):
    """Maneja la lógica para el formulario de editar post."""
    def handle_submit(self, form_data: dict):
        post_id_str = form_data.pop('post_id', None)
        if not post_id_str:
            print("Error: No se puede editar el post sin un ID.")
            return

        post_id = int(post_id_str)

        # 1. Si hay imágenes nuevas, las añadimos
        if self.uploaded_images:
            with rx.session() as session:
                for filename in self.uploaded_images:
                    session.add(PostImageModel(filename=filename, blog_post_id=post_id))
                session.commit()
        
        # 2. Actualizamos los otros campos del post
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post:
                post.title = form_data.get("title", post.title)
                post.content = form_data.get("content", post.content)
                post.publish_active = form_data.pop('publish_active', False) == "on"
                
                publish_date_str = form_data.pop('publish_date', None)
                publish_time_str = form_data.pop('publish_time', None)
                
                if publish_date_str and publish_time_str:
                    try:
                        post.publish_date = datetime.strptime(f"{publish_date_str} {publish_time_str}", "%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        post.publish_date = None # Si el formato es incorrecto, no se pone fecha
                else:
                    post.publish_date = None # Si no se envían los campos, se limpia la fecha

                session.add(post)
                session.commit()
        
        # 3. Recargamos el estado del post y redirigimos
        self.post = self._load_post_by_id(post_id)
        return self.to_blog_post()