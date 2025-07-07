from datetime import datetime
from typing import Optional, List, Dict, Any
import reflex as rx
import time

import sqlalchemy
from sqlmodel import select

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
    imagenes_temporales: List[str] = []
    form_data: Dict[str, str] = {}

    def set_form_field(self, field: str, value: str):
        """Actualiza los campos de texto del formulario (título y contenido)."""
        self.form_data[field] = value

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la carga de imágenes al directorio de uploads del servidor."""
        for file in files:
            upload_data = await file.read()
            # Usamos filename para consistencia entre navegadores
            path = rx.get_upload_dir() / file.filename
            with path.open("wb") as f:
                f.write(upload_data)
            
            if file.filename not in self.imagenes_temporales:
                self.imagenes_temporales.append(file.filename)

    def eliminar_imagen_temp(self, img_name: str):
        """Elimina una imagen de la lista de previsualización."""
        self.imagenes_temporales.remove(img_name)

    def publicar_post(self):
        """
        Crea el post en memoria, lo añade a la lista 'posts' y limpia el formulario.
        """
        if not self.form_data.get("title") or not self.form_data.get("content"):
            return rx.window_alert("Por favor, rellena el título y el contenido.")
            
        nuevo_post = {
            "title": self.form_data.get("title", "Sin Título"),
            "content": self.form_data.get("content", ""),
            "images": self.imagenes_temporales.copy(),
            # Usamos el timestamp como un ID simple y único para poder borrarlo
            "id": int(time.time() * 1000)
        }
        self.posts.append(nuevo_post)
        
        # Limpiar el estado para el siguiente post
        self.imagenes_temporales = []
        self.form_data = {}
        
        # Redirige al usuario a la página principal del blog
        return rx.redirect("/blog")

    def eliminar_post(self, post_id: int):
        """Encuentra y elimina un post de la lista en memoria usando su ID."""
        self.posts = [p for p in self.posts if p.get("id") != post_id]

    @rx.var
    def blog_post_id(self) -> str:  # Añadida la anotación de tipo -> str
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_url(self) -> str: # Añadida la anotación de tipo -> str
        if not self.post:
            return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}"

    @rx.var
    def blog_post_edit_url(self) -> str: # Añadida la anotación de tipo -> str
        if not self.post:
            return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None
            self.post_content = ""
            self.post_publish_active = False
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
                sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
            ).where(lookups)
            result = session.exec(sql_statement).one_or_none()
            # if result.userinfo: # db lookup
            #     print('working')
            #     result.userinfo.user
            self.post = result
            if result is None:
                self.post_content = ""
                return
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active

    def load_posts(self, *args, **kwargs):
        # if published_only:
        #     lookup_args = (
        #         (BlogPostModel.publish_active == True) &
        #         (BlogPostModel.publish_date < datetime.now())
        #     )
        with rx.session() as session:
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id)
            ).all()
            self.posts = result

    def add_post(self, form_data: dict):
        with rx.session() as session:
            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

# En full_stack_python/blog/state.py

    def save_post_edits(self, post_id: int, updated_data: dict):
        with rx.session() as session:
            post = session.exec(
                select(BlogPostModel).where(
                    BlogPostModel.id == post_id
                )
            ).one_or_none()
            if post is None:
                return
            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            
            # --- MEJORA ---
            # Después de guardar, recargamos el post con sus relaciones (userinfo y user)
            # para asegurar que el estado (self.post) esté completo antes de redirigir.
            reloaded_post = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(BlogPostModel.id == post_id)
            ).one_or_none()
            self.post = reloaded_post

    def to_blog_post(self, edit_page=False):
        if not self.post:
            return rx.redirect(BLOG_POSTS_ROUTE)
        if edit_page:
            return rx.redirect(f"{self.blog_post_edit_url}")
        return rx.redirect(f"{self.blog_post_url}")


class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}

    def handle_submit(self, form_data):
        data = form_data.copy()
        if self.my_userinfo_id is not None:
            data['userinfo_id'] = self.my_userinfo_id
        self.form_data = data
        self.add_post(data)
        return self.to_blog_post(edit_page=True)


class BlogEditFormState(BlogPostState):
    form_data: dict = {}

    @rx.var
    def publish_display_date(self) -> str:
        if not self.post:
            return datetime.now().strftime("%Y-%m-%d")
        if not self.post.publish_date:
            return datetime.now().strftime("%Y-%m-%d")
        return self.post.publish_date.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if not self.post:
            return datetime.now().strftime("%H:%M:%S")
        if not self.post.publish_date:
            return datetime.now().strftime("%H:%M:%S")
        return self.post.publish_date.strftime("%H:%M:%S")

    def handle_submit(self, form_data):
        self.form_data = form_data
        post_id = form_data.pop('post_id')
        publish_date = None
        if 'publish_date' in form_data:
            publish_date = form_data.pop('publish_date')
        publish_time = None
        if 'publish_time' in form_data:
            publish_time = form_data.pop('publish_time')
        publish_input_string = f"{publish_date} {publish_time}"
        try:
            final_publish_date = datetime.strptime(publish_input_string, "%Y-%m-%d %H:%M:%S")
        except:
            final_publish_date = None
        publish_active = False
        if 'publish_active' in form_data:
            publish_active = form_data.pop('publish_active') == "on"
        updated_data = {**form_data}
        updated_data['publish_active'] = publish_active
        updated_data['publish_date'] = final_publish_date
        self.save_post_edits(post_id, updated_data)
        return self.to_blog_post()