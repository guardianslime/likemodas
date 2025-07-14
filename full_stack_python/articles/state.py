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

class ArticlePublicState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    limit: int = 20

    @rx.var
    def post_id(self) -> str:
        return self.router.params.get("article_id", "")

    @rx.var
    def post_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{ARTICLE_LIST_ROUTE}/{self.post.id}"
        return ARTICLE_LIST_ROUTE

    def get_post_detail(self):
        try:
            post_id_int = int(self.post_id)
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
