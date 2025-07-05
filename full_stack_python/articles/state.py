# full_stack_python/articles/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel

ARTICLE_LIST_ROUTE = navigation.routes.ARTICLE_LIST_ROUTE
if ARTICLE_LIST_ROUTE.endswith("/"):
    ARTICLE_LIST_ROUTE = ARTICLE_LIST_ROUTE[:-1]

class ArticlePublicState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    limit: int = 20

    @rx.var
    def post_images(self) -> list[PostImageModel]:
        """Devuelve de forma segura la lista de imágenes del post, o una lista vacía."""
        if self.post and self.post.images:
            return self.post.images
        return []

    @rx.var
    def post_id(self) -> str:
        return self.router.page.params.get("article_id", "")

    @rx.var
    def post_url(self) -> str:
        if not self.post: return f"{ARTICLE_LIST_ROUTE}"
        return f"{ARTICLE_LIST_ROUTE}/{self.post.id}"

    def get_post_detail(self):
        with rx.session() as session:
            if self.post_id == "":
                self.post = None; return
            self.post = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(
                    (BlogPostModel.publish_active == True) &
                    (BlogPostModel.publish_date < datetime.now()) &
                    (BlogPostModel.id == self.post_id)
                )
            ).one_or_none()

    # --- ¡MÉTODO RESTAURADO! ---
    # Esta es la función que faltaba.
    def set_limit_and_reload(self, new_limit: int = 5):
        self.limit = new_limit
        return self.load_posts()

    def load_posts(self, *args, **kwargs):
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(
                    (BlogPostModel.publish_active == True) &
                    (BlogPostModel.publish_date < datetime.now())
                ).limit(self.limit)
            ).all()

    def to_post(self):
        if not self.post:
            return rx.redirect(ARTICLE_LIST_ROUTE)
        return rx.redirect(self.post_url)