# full_stack_python/blog/state.py (VERSIÓN UNIFICADA)

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
    """Un único estado para manejar los blog posts desde la base de datos."""
    posts: List[BlogPostModel] = []
    post: Optional[BlogPostModel] = None

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}"
        return BLOG_POSTS_ROUTE

    @rx.var
    def blog_post_edit_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"
        return BLOG_POSTS_ROUTE

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None
            return
            
        with rx.session() as session:
            try:
                post_id_int = int(self.blog_post_id)
                lookups = (
                    (BlogPostModel.userinfo_id == self.my_userinfo_id) & 
                    (BlogPostModel.id == post_id_int)
                )
                result = session.exec(
                    select(BlogPostModel).options(
                        sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                    ).where(lookups)
                ).one_or_none()
                self.post = result
            except (ValueError, TypeError):
                self.post = None

    def load_posts(self):
        if self.my_userinfo_id is None:
            self.posts = []
            return
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo))
                .where(BlogPostModel.userinfo_id == self.my_userinfo_id)
                .order_by(BlogPostModel.created_at.desc())
            ).all()

    def _add_post_to_db(self, form_data: dict):
        with rx.session() as session:
            post_data = form_data.copy()
            post_data['userinfo_id'] = self.my_userinfo_id
            post = BlogPostModel(**post_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def _save_post_edits_to_db(self, post_id: int, updated_data: dict):
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

class BlogAddFormState(BlogPostState):
    def handle_submit(self, form_data: dict):
        if self.my_userinfo_id is None:
            return rx.window_alert("Error: Debes iniciar sesión para crear un post.")
        self._add_post_to_db(form_data)
        return rx.redirect(self.blog_post_edit_url)

class BlogEditFormState(BlogPostState):
    post_content: str = ""
    post_publish_active: bool = False

    def on_load_edit(self):
        """Carga el detalle del post y también el contenido en el estado del formulario."""
        self.get_post_detail()
        if self.post:
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active

    @rx.var
    def publish_display_date(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%Y-%m-%d")
        return self.post.publish_date.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%H-%M-%S")
        return self.post.publish_date.strftime("%H:%M:%S")

    def handle_submit(self, form_data: dict):
        post_id = int(form_data.pop('post_id'))
        
        final_publish_date = None
        if form_data.get('publish_date') and form_data.get('publish_time'):
            try:
                dt_str = f"{form_data['publish_date']} {form_data['publish_time']}"
                final_publish_date = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        
        form_data['publish_active'] = form_data.get('publish_active') == "on"
        form_data['publish_date'] = final_publish_date
        
        # Eliminar claves que no son del modelo antes de guardar
        form_data.pop('publish_time', None)
        
        self._save_post_edits_to_db(post_id, form_data)
        return rx.redirect(self.blog_post_url)