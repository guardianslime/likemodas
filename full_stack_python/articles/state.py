from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo

ARTICLE_LIST_ROUTE = navigation.routes.ARTICLE_LIST_ROUTE
if ARTICLE_LIST_ROUTE.endswith("/"):
    ARTICLE_LIST_ROUTE = ARTICLE_LIST_ROUTE[:-1]

class ArticleDetailState(SessionState):
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.var
    def imagen_actual(self) -> str:
        if self.post and self.post.images and len(self.post.images) > self.img_idx:
            return self.post.images[self.img_idx]
        return ""

    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.event
    def on_load(self):
        # --- ✨ CORRECCIÓN DE SERIALIZACIÓN ✨ ---
        # Se lee el parámetro directamente del router, no de una @rx.var
        article_id_str = self.router.page.params.get("article_id", "")
        try:
            pid = int(article_id_str)
        except (ValueError, TypeError):
            return
        with rx.session() as session:
            self.post = session.get(BlogPostModel, pid)
        self.img_idx = 0

    @rx.event
    def siguiente_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx + 1) % len(self.post.images)

    @rx.event
    def anterior_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx - 1 + len(self.post.images)) % len(self.post.images)

class ArticlePublicState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    limit: int = 20

    def get_post_detail(self):
        # --- ✨ CORRECCIÓN DE SERIALIZACIÓN ✨ ---
        post_id_str = self.router.page.params.get("article_id", "")
        try:
            post_id_int = int(post_id_str)
        except (ValueError, TypeError):
            self.post = None
            return
        lookups = (
            (BlogPostModel.publish_active == True) &
            (BlogPostModel.publish_date < datetime.now()) &
            (BlogPostModel.id == post_id_int)
        )
        with rx.session() as session:
            sql_statement = select(BlogPostModel).options(
                sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
            ).where(lookups)
            self.post = session.exec(sql_statement).one_or_none()

    def set_limit_and_reload(self, new_limit: int = 5):
        self.limit = new_limit
        yield type(self).load_posts()

    def load_posts(self, *args, **kwargs):
        lookup_args = (
            (BlogPostModel.publish_active == True) &
            (BlogPostModel.publish_date < datetime.now())
        )
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo))
                .where(lookup_args)
                .limit(self.limit)
            ).all()