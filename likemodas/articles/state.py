# likemodas/articles/state.py (VERSIÓN CORREGIDA)

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, CommentModel


ARTICLE_LIST_ROUTE = navigation.routes.ARTICLE_LIST_ROUTE
if ARTICLE_LIST_ROUTE.endswith("/"):
    ARTICLE_LIST_ROUTE = ARTICLE_LIST_ROUTE[:-1]


class ArticleDetailState(SessionState):
    # ... (esta clase no cambia)
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.var
    def post_id_from_route(self) -> str:
        return self.router.page.params.get("article_id", "")

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
        try:
            pid = int(self.post_id_from_route)
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
    """Estado UNIFICADO para la lista pública de artículos."""
    posts: List["BlogPostModel"] = []
    limit: int = 100 # Aumentado el límite para mostrar todos los productos

    # ✨ --- MÉTODO CORREGIDO Y CENTRALIZADO --- ✨
    @rx.event
    def load_posts(self):
        """Carga las publicaciones Y sus comentarios para TODAS las páginas públicas."""
        lookup_args = (
            (BlogPostModel.publish_active == True) &
            (BlogPostModel.publish_date < datetime.now())
        )
        with rx.session() as session:
            statement = (
                select(BlogPostModel)
                .options(
                    # Se añade la carga de comentarios para que las estrellas funcionen
                    sqlalchemy.orm.joinedload(BlogPostModel.comments)
                )
                .where(lookup_args)
                .order_by(BlogPostModel.created_at.desc())
                .limit(self.limit)
            )
            self.posts = session.exec(statement).unique().all()