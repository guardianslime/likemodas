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
    
    @rx.var
    def post_images(self) -> list[PostImageModel]:
        if self.post and self.post.images:
            return self.post.images
        return []

    @rx.var
    def post_id(self) -> str:
        return self.router.page.params.get("article_id", "")

    def get_post_detail(self):
        with rx.session() as session:
            if self.post_id == "":
                self.post = None
                return
            
            # --- ¡CORRECCIÓN AQUÍ! ---
            # Añadimos .options(sqlalchemy.orm.selectinload(BlogPostModel.images))
            # para cargar las imágenes junto con el post.
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(
                    (BlogPostModel.publish_active == True) &
                    (BlogPostModel.publish_date < datetime.now()) &
                    (BlogPostModel.id == self.post_id)
                )
            ).one_or_none()
            self.post = result

    def load_posts(self, *args, **kwargs):
        lookup_args = (
            (BlogPostModel.publish_active == True) &
            (BlogPostModel.publish_date < datetime.now())
        )
        with rx.session() as session:
            # --- ¡CORRECCIÓN AQUÍ! ---
            # También cargamos las imágenes para la lista de artículos.
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(lookup_args).limit(self.limit)
            ).all()
            self.posts = result