from datetime import datetime
from typing import Optional, List
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
    """Manages all state for blog posts."""
    posts: List[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    post_content: str = ""
    post_publish_active: bool = False

    @rx.var
    def blog_post_id(self) -> str:
        """Get the blog_id from the URL parameters."""
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_url(self) -> str:
        """The URL for the current blog post."""
        if not self.post:
            return BLOG_POSTS_ROUTE
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}"

    @rx.var
    def blog_post_edit_url(self) -> str:
        """The URL to edit the current blog post."""
        if not self.post:
            return BLOG_POSTS_ROUTE
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"

    def get_post_detail(self):
        """
        Carga los detalles de un post para la página de detalles.
        Esta función está diseñada para ser pública; no filtra por usuario
        para que cualquiera pueda ver un post. El control de edición se hace en la UI.
        """
        with rx.session() as session:
            if not self.blog_post_id:
                self.post = None
                return

            # Carga el post y la información del usuario asociada.
            sql_statement = select(BlogPostModel).options(
                sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
            ).where(BlogPostModel.id == self.blog_post_id)
            
            result = session.exec(sql_statement).one_or_none()
            self.post = result
            if result:
                self.post_content = self.post.content
                self.post_publish_active = self.post.publish_active
            else:
                self.post_content = ""

    def load_posts(self, *args, **kwargs):
        """Carga la lista de posts que pertenecen al usuario logueado."""
        with rx.session() as session:
            # Asegurarse que el usuario está logueado para cargar sus posts.
            if self.my_userinfo_id is None:
                self.posts = []
                return
            
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id)
            ).all()
            self.posts = result

    def add_post(self, form_data: dict):
        """Añade un nuevo post a la base de datos."""
        with rx.session() as session:
            post = BlogPostModel(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def save_post_edits(self, post_id: int, updated_data: dict):
        """Guarda los cambios de un post editado."""
        with rx.session() as session:
            # Usar session.get() es la forma más directa de obtener un objeto por su ID.
            post = session.get(BlogPostModel, post_id)
            if post is None:
                print(f"Error: No se encontró el post con id {post_id}")
                return
            
            # Solo actualizar si el post pertenece al usuario
            if post.userinfo_id != self.my_userinfo_id:
                print("Error: El usuario no tiene permiso para editar este post.")
                return

            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def to_blog_post(self, edit_page=False):
        """Redirige a la página de detalle o edición del post actual."""
        if not self.post:
            return rx.redirect(BLOG_POSTS_ROUTE)
        if edit_page:
            return rx.redirect(self.blog_post_edit_url)
        return rx.redirect(self.blog_post_url)


class BlogAddPostFormState(BlogPostState):
    """Maneja el formulario para añadir nuevos posts."""
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        data = form_data.copy()
        if self.my_userinfo_id:
            data['userinfo_id'] = self.my_userinfo_id
        # Un post nuevo siempre se crea como no activo y sin fecha de publicación.
        data['publish_active'] = False
        data['publish_date'] = None
        self.add_post(data)
        # Redirige a la página de edición para que el usuario pueda terminarlo.
        return self.to_blog_post(edit_page=True)


class BlogEditFormState(BlogPostState):
    """Maneja el formulario para editar posts existentes."""
    form_data: dict = {}

    @rx.var
    def publish_display_date(self) -> str:
        """Formatea la fecha para el input de tipo 'date'."""
        date_to_show = self.post.publish_date if self.post and self.post.publish_date else datetime.now()
        return date_to_show.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        """Formatea la hora para el input de tipo 'time'."""
        time_to_show = self.post.publish_date if self.post and self.post.publish_date else datetime.now()
        return time_to_show.strftime("%H:%M")

    def handle_submit(self, form_data: dict):
        """Procesa y guarda los datos del formulario de edición."""
        post_id = int(form_data.pop('post_id'))
        
        updated_data = {
            'title': form_data.get('title'),
            'content': form_data.get('content')
        }

        # Lógica robusta para manejar la fecha y hora
        publish_active = form_data.get('publish_active') == "on"
        updated_data['publish_active'] = publish_active
        
        final_publish_date = None

        if publish_active:
            publish_date_str = form_data.get('publish_date')
            publish_time_str = form_data.get('publish_time')

            if publish_date_str and publish_time_str:
                publish_input_string = f"{publish_date_str} {publish_time_str}"
                try:
                    # strptime convierte el string a un objeto datetime
                    final_publish_date = datetime.strptime(publish_input_string, "%Y-%m-%d %H:%M")
                except ValueError:
                    # Si el formato es inválido, mantenemos la fecha que ya existía.
                    print(f"Error al convertir la fecha y hora: {publish_input_string}")
                    final_publish_date = self.post.publish_date if self.post else None
            else:
                # Si el switch está activo pero no hay fecha/hora, usamos la hora actual.
                final_publish_date = datetime.now()
        
        updated_data['publish_date'] = final_publish_date

        self.save_post_edits(post_id, updated_data)
        return self.to_blog_post()
