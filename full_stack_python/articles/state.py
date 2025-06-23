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
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    post_content: str = ""
    post_publish_active: bool = False

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
        with rx.session() as session:
            if not self.blog_post_id:
                self.post = None
                return

            # --- CORRECCIÓN: Cargar el post por ID sin filtrar por usuario ---
            # Esto permite que cualquier persona vea el post, no solo el autor.
            # El control de edición ya se hace en la propia página de detalles.
            sql_statement = select(BlogPostModel).options(
                sqlalchemy.orm.joinedload(BlogPost.userinfo).joinedload(UserInfo.user)
            ).where(BlogPostModel.id == self.blog_post_id)
            
            result = session.exec(sql_statement).one_or_none()
            self.post = result
            if result is None:
                self.post_content = ""
                return
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active

    def load_posts(self, *args, **kwargs):
        with rx.session() as session:
            # Cargar todos los posts del usuario logueado
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

    def save_post_edits(self, post_id: int, updated_data: dict):
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post is None:
                return
            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def to_blog_post(self, edit_page=False):
        if not self.post:
            return rx.redirect(BLOG_POSTS_ROUTE)
        if edit_page:
            return rx.redirect(self.blog_post_edit_url)
        return rx.redirect(self.blog_post_url)


class BlogAddPostFormState(BlogPostState):
    form_data: dict = {}

    def handle_submit(self, form_data):
        data = form_data.copy()
        if self.my_userinfo_id is not None:
            data['userinfo_id'] = self.my_userinfo_id
        # Establecer una fecha de publicación por defecto al crear
        data['publish_date'] = datetime.now()
        self.form_data = data
        self.add_post(data)
        return self.to_blog_post(edit_page=True)


class BlogEditFormState(BlogPostState):
    form_data: dict = {}

    @rx.var
    def publish_display_date(self) -> str:
        date_to_show = self.post.publish_date if self.post and self.post.publish_date else datetime.now()
        return date_to_show.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        time_to_show = self.post.publish_date if self.post and self.post.publish_date else datetime.now()
        # Usamos HH:MM que es el formato estándar para input type='time'
        return time_to_show.strftime("%H:%M")

    def handle_submit(self, form_data):
        post_id = form_data.pop('post_id')
        
        # Copiamos el resto de los datos (title, content)
        updated_data = form_data.copy()

        # --- CORRECCIÓN: Lógica robusta para manejar la fecha y hora ---
        publish_active = form_data.get('publish_active') == "on"
        updated_data['publish_active'] = publish_active
        
        final_publish_date = None

        if publish_active:
            publish_date_str = form_data.get('publish_date')
            publish_time_str = form_data.get('publish_time')

            # Solo procesar si ambos campos tienen valor
            if publish_date_str and publish_time_str:
                # Añadimos segundos si no están para que el formato coincida
                if len(publish_time_str.split(':')) == 2:
                    publish_time_str += ':00'
                
                publish_input_string = f"{publish_date_str} {publish_time_str}"
                try:
                    final_publish_date = datetime.strptime(publish_input_string, "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    print(f"Error al convertir la fecha: {e}")
                    # Si hay un error, podríamos mantener la fecha existente en lugar de ponerla a None
                    final_publish_date = self.post.publish_date if self.post else None
        
        # Asignar la fecha final (puede ser un datetime o None si el post no está activo)
        updated_data['publish_date'] = final_publish_date

        self.save_post_edits(post_id, updated_data)
        return self.to_blog_post()

