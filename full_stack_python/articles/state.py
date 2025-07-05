# full_stack_python/articles/state.py
from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel

class ArticlePublicState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    limit: int = 10

    @rx.var
    def post_id(self) -> int:
        try:
            return int(self.router.page.params.get("article_id", 0))
        except:
            return 0

    def get_post_detail(self):
        with rx.session() as session:
            if not self.post_id: self.post = None; return
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

    def load_posts(self):
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo),
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(
                    (BlogPostModel.publish_active == True) &
                    (BlogPostModel.publish_date < datetime.now())
                ).order_by(BlogPostModel.publish_date.desc()).limit(self.limit)
            ).all()