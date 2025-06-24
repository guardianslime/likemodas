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

# --- ESTADO PARA POSTS PÚBLICOS ---
# Este estado se encarga de cargar y mostrar los posts que están marcados como 'publish_active'.
class ArticlePublicState(rx.State):
    posts: list[BlogPostModel] = []
    limit: int = 100 # Por defecto, muestra 100 posts

    def load_posts(self, limit: int | None = None):
        """Carga todos los posts que están publicados."""
        if limit is not None:
            self.limit = limit
        with rx.session() as session:
            # Selecciona los posts donde 'publish_active' es verdadero.
            self.posts = session.exec(
                select(BlogPostModel)
                .where(BlogPostModel.publish_active == True)
                .order_by(BlogPostModel.publish_date.desc()) # Ordena por fecha de publicación
                .limit(self.limit)
            ).all()

# --- ESTADO PARA LOS POSTS PRIVADOS Y LA EDICIÓN ---
# (Este es el código que ya habíamos corregido antes, asegúrate que se quede así)
class BlogPostState(SessionState):
    """Manages all state for blog posts."""
    posts: List[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    post_content: str = ""
    post_publish_active: bool = False

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_url(self) -> str:
        if not self.post:
            return BLOG_POSTS_ROUTE
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}"

    @rx.var
    def blog_post_edit_url(self) -> str:
        if not self.post:
            return BLOG_POSTS_ROUTE
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"

    def get_post_detail(self):
        with rx.session() as session:
            if not self.blog_post_id:
                self.post = None
                return

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
        with rx.session() as session:
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
            if post.userinfo_id != self.my_userinfo_id:
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

    def handle_submit(self, form_data: dict):
        data = form_data.copy()
        if self.my_userinfo_id:
            data['userinfo_id'] = self.my_userinfo_id
        data['publish_active'] = False
        data['publish_date'] = None
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
        return time_to_show.strftime("%H:%M")

    def handle_submit(self, form_data: dict):
        post_id = int(form_data.pop('post_id'))
        
        updated_data = {
            'title': form_data.get('title'),
            'content': form_data.get('content')
        }

        publish_active = form_data.get('publish_active') == "on"
        updated_data['publish_active'] = publish_active
        
        final_publish_date = None

        if publish_active:
            publish_date_str = form_data.get('publish_date')
            publish_time_str = form_data.get('publish_time')

            if publish_date_str and publish_time_str:
                publish_input_string = f"{publish_date_str} {publish_time_str}"
                try:
                    final_publish_date = datetime.strptime(publish_input_string, "%Y-%m-%d %H:%M")
                except ValueError:
                    print(f"Error al convertir la fecha y hora: {publish_input_string}")
                    final_publish_date = self.post.publish_date if self.post else None
            else:
                final_publish_date = datetime.now()
        
        updated_data['publish_date'] = final_publish_date

        self.save_post_edits(post_id, updated_data)
        return self.to_blog_post()
