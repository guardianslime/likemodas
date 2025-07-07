# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
import os

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel # Importar PostImageModel

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE
if BLOG_POSTS_ROUTE.endswith("/"):
    BLOG_POSTS_ROUTE = BLOG_POSTS_ROUTE[:-1]

class BlogPostState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    
    # Declaramos explícitamente post_content aquí.
    post_content: str = ""
    # También declaramos la variable para el switch de publicación
    post_publish_active: bool = False
    
    imagenes_temporales: list[str] = []
 
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
        
    # --- MÉTODOS PARA MANEJAR LA CARGA DE IMÁGENES ---
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.filename # Usar filename en lugar de name
            with path.open("wb") as f:
                f.write(data)
            if file.filename not in self.imagenes_temporales:
                self.imagenes_temporales.append(file.filename)

    @rx.event
    def eliminar_imagen_temp(self, nombre: str):
        if nombre in self.imagenes_temporales:
            self.imagenes_temporales.remove(nombre)
            # Opcional: Borrar el archivo del servidor si ya no se va a usar
            # path = rx.get_upload_dir() / nombre
            # if path.exists():
            #     os.remove(path)

    def get_post_detail(self):
        """Al cargar el post, también poblamos las variables de estado del formulario."""
        if self.my_userinfo_id is None:
            return
        
        with rx.session() as session:
            if not self.blog_post_id:
                self.post = None
                return
            
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
            # Si el post se carga con éxito, actualizamos las otras variables
            if self.post:
                self.post_content = self.post.content
                self.post_publish_active = self.post.publish_active
            else:
                self.post_content = ""
                self.post_publish_active = False

    def load_posts(self, *args, **kwargs):
        """Carga solo los posts del usuario autenticado."""
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.images) # Cargar imágenes para la portada
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id)
                 .order_by(BlogPostModel.id.desc())
            ).all()

    def add_post(self, form_data: dict):
        """Añade el post y sus imágenes a la BD."""
        with rx.session() as session:
            # Crear la entrada del post
            post = BlogPostModel(
                title=form_data.get("title", "Sin Título"),
                content=form_data.get("content", ""),
                userinfo_id=self.my_userinfo_id
            )
            session.add(post)
            session.commit()
            session.refresh(post)

            # Asociar las imágenes temporales con el post recién creado
            for img_name in self.imagenes_temporales:
                image_entry = PostImageModel(img_name=img_name, post_id=post.id)
                session.add(image_entry)
            
            session.commit()
            self.post = post

        # Limpiar las imágenes temporales después de publicar
        self.imagenes_temporales = []


    def delete_post(self, post_id: int):
        """Elimina un post, sus imágenes de la BD y los archivos del servidor."""
        with rx.session() as session:
            # Encontrar el post con sus imágenes
            post_to_delete = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.images)
                ).where(BlogPostModel.id == post_id)
            ).one_or_none()

            if post_to_delete and post_to_delete.userinfo_id == self.my_userinfo_id:
                # 1. Borrar archivos de imagen del servidor
                upload_dir = rx.get_upload_dir()
                for image in post_to_delete.images:
                    file_path = upload_dir / image.img_name
                    if file_path.exists():
                        os.remove(file_path)

                # 2. Borrar el post (SQLModel se encarga de borrar en cascada las imágenes gracias a la configuración)
                session.delete(post_to_delete)
                session.commit()
        
        # 3. Recargar la lista de posts para actualizar la UI
        self.load_posts()


    def save_post_edits(self, post_id: int, updated_data: dict):
        # Esta función ya existe, la dejamos como está pero nos aseguramos
        # de que la lógica de edición de imágenes se maneje aquí si es necesario.
        # Por ahora, nos enfocaremos en añadir y borrar.
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post and post.userinfo_id == self.my_userinfo_id:
                for key, value in updated_data.items():
                    setattr(post, key, value)
                session.add(post)
                session.commit()
                session.refresh(post)
                self.post = post

    def to_blog_list(self):
        return rx.redirect(BLOG_POSTS_ROUTE)
        
    def to_blog_post(self, edit_page=False):
        if not self.post:
            return rx.redirect(BLOG_POSTS_ROUTE)
        if edit_page:
            return rx.redirect(f"{self.blog_post_edit_url}")
        return rx.redirect(f"{self.blog_post_url}")

# --- ESTADO PARA FORMULARIO DE AÑADIR ---
class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        if self.my_userinfo_id is None:
            return rx.window_alert("Error: Debes iniciar sesión para publicar.")
        
        self.add_post(form_data)
        return rx.redirect(BLOG_POSTS_ROUTE)


# --- NUEVO ESTADO PARA LA PÁGINA PÚBLICA ---
class BlogPublicState(SessionState):
    """Gestiona la carga de todos los posts para la vista pública."""
    posts: List[BlogPostModel] = []
    post: Optional[BlogPostModel] = None

    @rx.var
    def current_blog_id(self) -> str:
        """Obtiene el ID del post desde la URL, que viene como 'blog_id'."""
        return self.router.page.params.get("blog_id", "")

    def load_all_posts(self):
        """Carga todos los posts de todos los usuarios."""
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.images),
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                ).order_by(BlogPostModel.id.desc())
            ).all()

    def get_post_detail(self):
        """Obtiene el detalle de un post público."""
        with rx.session() as session:
            self.post = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.images),
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(BlogPostModel.id == self.article_id)
            ).one_or_none()

# (Las clases BlogEditFormState se mantienen igual, no necesitan cambios directos por ahora)
class BlogEditFormState(BlogPostState):
    # ... código existente ...
    pass