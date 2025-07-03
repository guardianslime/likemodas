# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List, Any
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
    posts: List[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    post_content: str = ""
    post_publish_active: bool = False
    # Almacena las rutas de las imágenes subidas para la vista previa.
    img: list[str] = []

    # --- CORRECCIÓN ---
    # Lógica de subida de imágenes simplificada para Reflex 0.8.0.
    async def handle_upload(self, files: list[rx.UploadFile]):
        """
        Maneja los archivos que Reflex ya subió automáticamente.
        Solo necesitamos guardar sus nombres en el estado.
        """
        for file in files:
            # Los archivos ya están en .web/public, solo guardamos la ruta.
            self.img.append(f"/{file.filename}")
        return

    def add_post(self, form_data: dict):
        """Añade un nuevo post a la BD, incluyendo la URL de la imagen si existe."""
        with rx.session() as session:
            # Si se subió una imagen, se añade su URL.
            if self.img:
                form_data['image_url'] = self.img[0]

            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post
            self.img = [] # Se limpia la lista de imágenes después de usarla.

    def save_post_edits(self, post_id: int, updated_data: dict):
        """Guarda las ediciones de un post, incluyendo una posible nueva imagen."""
        with rx.session() as session:
            post = session.exec(select(BlogPostModel).where(BlogPostModel.id == post_id)).one_or_none()
            if post is None:
                return
            
            # Si se subió una nueva imagen, se actualiza la URL.
            if self.img:
                updated_data['image_url'] = self.img[0]

            for key, value in updated_data.items():
                setattr(post, key, value)
            
            session.add(post)
            session.commit()
            self.img = [] # Se limpia la lista de imágenes

            # Se recarga el post para asegurar que los datos estén actualizados.
            self.post = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(BlogPostModel.id == post_id)
            ).one_or_none()

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

    def get_post_detail(self):
        """Obtiene los detalles de un post específico para el usuario actual."""
        if self.my_userinfo_id is None or not self.blog_post_id:
            self.post = None
            return

        with rx.session() as session:
            lookups = (
                (BlogPostModel.userinfo_id == self.my_userinfo_id) &
                (BlogPostModel.id == self.blog_post_id)
            )
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(lookups)
            ).one_or_none()
            
            self.post = result
            if result:
                self.post_content = result.content
                self.post_publish_active = result.publish_active
            else:
                self.post_content = ""

    def load_posts(self, *args, **kwargs):
        """Carga todos los posts del usuario autenticado."""
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id)
            ).all()

    def to_blog_post(self, edit_page=False):
        if not self.post:
            return rx.redirect(BLOG_POSTS_ROUTE)
        return rx.redirect(self.blog_post_edit_url if edit_page else self.blog_post_url)


class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}

    def handle_submit(self, form_data):
        """Maneja el envío del formulario para crear un post."""
        data = form_data.copy()
        if self.my_userinfo_id is not None:
            data['userinfo_id'] = self.my_userinfo_id
        self.form_data = data
        self.add_post(data)
        return self.to_blog_post(edit_page=True)


class BlogEditFormState(BlogPostState):
    form_data: dict = {}

    # ... (El resto de la clase no necesita cambios) ...