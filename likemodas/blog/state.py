# likemodas/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select, Field

# Se importa el estado BASE
from ..auth.state import SessionState

from .. import navigation
from ..models import (
    BlogPostModel, UserInfo, CommentModel, CommentVoteModel, VoteType,
    PurchaseModel, PurchaseItemModel, PurchaseStatus, Category
)
from ..data.product_options import (
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES
)

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

class BlogPostState(SessionState):
    """Estado para la lista y detalle de posts del admin."""
    posts: list[BlogPostModel] = Field(default_factory=list)
    post: Optional[BlogPostModel] = None
    search_query: str = ""

    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return self.post.price_cop
        return "$0"

    @rx.var
    def blog_post_edit_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"
        return BLOG_POSTS_ROUTE

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def filtered_posts(self) -> list[BlogPostModel]:
        if not self.search_query.strip():
            return self.posts
        return [
            post for post in self.posts
            if self.search_query.lower() in post.title.lower()
        ]

    @rx.var
    def categories(self) -> list[str]:
        return [c.value for c in Category]

    @rx.event
    def load_posts(self):
        if not self.is_admin or self.my_userinfo_id is None:
            self.posts = []
            return
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .where(BlogPostModel.userinfo_id == int(self.my_userinfo_id))
                .order_by(BlogPostModel.created_at.desc())
            ).all()

    @rx.event
    def get_post_detail(self):
        if not self.is_admin or self.my_userinfo_id is None:
            self.post = None
            return
        try:
            post_id_int = int(self.blog_post_id)
        except (ValueError, TypeError):
            self.post = None
            return
        with rx.session() as session:
            self.post = session.get(BlogPostModel, post_id_int)

    @rx.event
    def delete_post(self, post_id: int):
        if not self.is_admin or self.my_userinfo_id is None: return
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == int(self.my_userinfo_id):
                session.delete(post_to_delete)
                session.commit()
        return rx.redirect(BLOG_POSTS_ROUTE)

class BlogAddFormState(SessionState):
    """Estado para el formulario de AÑADIR posts."""
    title: str = ""
    content: str = ""
    price: float = 0.0
    category: str = ""
    temp_images: list[str] = Field(default_factory=list)

    # ... (resto de atributos de formulario)
    talla: str = ""
    tipo_tela: str = ""
    color_ropa: str = ""
    tipo_prenda: str = ""
    numero_calzado: str = ""
    # ...

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            if file.name not in self.temp_images:
                self.temp_images.append(file.name)

    def _create_post(self, publish: bool) -> rx.event.EventSpec:
        if not self.is_admin or self.my_userinfo_id is None: return rx.toast.error("No tienes permiso.")
        # ... (resto de la lógica de creación)
        with rx.session() as session:
            post = BlogPostModel(
                title=self.title.strip(), content=self.content.strip(),
                price=self.price, image_urls=self.temp_images.copy(),
                userinfo_id=int(self.my_userinfo_id),
                publish_active=publish,
                # ... (resto de atributos)
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            new_post_id = post.id
        
        self.reset()
        return rx.redirect(f"/blog/{new_post_id}")

    @rx.event
    def submit(self):
        return self._create_post(publish=False)

    @rx.event
    def submit_and_publish(self):
        return self._create_post(publish=True)


class BlogEditFormState(SessionState):
    """Estado para el formulario de EDITAR posts."""
    post: Optional[BlogPostModel] = None
    post_content: str = ""
    post_publish_active: bool = False
    price_str: str = "0.0"
    
    # ... (resto de la clase)

class CommentState(SessionState):
    """Estado que maneja tanto la vista del post público como sus comentarios."""
    post: Optional[BlogPostModel] = None
    comments: list[CommentModel] = Field(default_factory=list)
    new_comment_text: str = ""
    new_comment_rating: int = 0

    @rx.event
    def on_load(self):
        # ... (lógica para cargar post y comentarios)
        pid = int(self.router.page.params.get("id", "0"))
        with rx.session() as session:
            db_post_result = session.exec(
                select(BlogPostModel)
                .options(
                    sqlalchemy.orm.joinedload(BlogPostModel.comments)
                    .joinedload(CommentModel.userinfo).joinedload(UserInfo.user),
                )
                .where(BlogPostModel.id == pid, BlogPostModel.publish_active == True)
            ).unique().one_or_none()
            if db_post_result:
                self.post = db_post_result
                self.comments = sorted(db_post_result.comments, key=lambda c: c.created_at, reverse=True)
    # ... (resto de la clase)