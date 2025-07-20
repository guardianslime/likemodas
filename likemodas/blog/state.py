# likemodas/blog/state.py (VERSIÓN FINAL Y DESACOPLADA)

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, CommentModel, CommentVoteModel, VoteType, PurchaseModel, PurchaseItemModel, PurchaseStatus

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

# --- ESTADOS PARA PÁGINAS DE ADMINISTRACIÓN ---

class BlogPostState(SessionState):
    """Estado para la lista y detalle de posts del admin."""
    posts: list[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.var
    def blog_post_edit_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"
        return BLOG_POSTS_ROUTE

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

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
        self.img_idx = 0

    @rx.event
    def delete_post(self, post_id: int):
        if not self.is_admin: return
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == int(self.my_userinfo_id):
                session.delete(post_to_delete)
                session.commit()
        return self.load_posts

class BlogAddFormState(SessionState):
    """Estado para el formulario de AÑADIR posts."""
    title: str = ""
    content: str = ""
    price: float = 0.0
    temp_images: list[str] = []

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            if file.name not in self.temp_images:
                self.temp_images.append(file.name)

    @rx.event
    def remove_image(self, name: str):
        if name in self.temp_images:
            self.temp_images.remove(name)
    
    @rx.event
    def set_price_from_input(self, value: str):
        try:
            self.price = float(value)
        except (ValueError, TypeError):
            self.price = 0.0

    @rx.event
    def submit(self):
        if not self.is_admin: return rx.window_alert("No tienes permiso.")
        if self.price <= 0: return rx.window_alert("El precio debe ser mayor a cero.")
        if not self.title.strip(): return rx.window_alert("El título no puede estar vacío.")

        with rx.session() as session:
            post = BlogPostModel(
                title=self.title.strip(), content=self.content.strip(),
                price=self.price, images=self.temp_images.copy(),
                userinfo_id=self.my_userinfo_id, publish_active=False,
                publish_date=datetime.utcnow()
            )
            session.add(post)
            session.commit()
        
        self.title, self.content, self.price, self.temp_images = "", "", 0.0, []
        return rx.redirect(BLOG_POSTS_ROUTE)

class BlogEditFormState(BlogPostState):
    """Estado para el formulario de EDITAR posts."""
    post_content: str = ""
    post_publish_active: bool = False
    price_str: str = "0.0"

    @rx.event
    def on_load_edit(self):
        self.get_post_detail()
        if self.post:
            self.post_content = self.post.content or ""
            self.post_publish_active = self.post.publish_active
            self.price_str = str(self.post.price or 0.0)

    @rx.event
    def set_price(self, value: str):
        self.price_str = value

    @rx.var
    def publish_display_date(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%Y-%m-%d")
        return self.post.publish_date.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%H:%M:%S")
        return self.post.publish_date.strftime("%H:%M:%S")

    @rx.event
    def handle_submit(self, form_data: dict):
        post_id = int(form_data.pop("post_id", 0))
        if not post_id or not self.is_admin:
            return rx.toast.error("No se puede guardar el post.")
        
        form_data["publish_active"] = form_data.get("publish_active") == "on"
        try:
            form_data["price"] = float(self.price_str)
        except ValueError:
            return rx.toast.error("Precio inválido.")
        
        if form_data.get("publish_date") and form_data.get("publish_time"):
            try:
                dt_str = f"{form_data['publish_date']} {form_data['publish_time']}"
                form_data["publish_date"] = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                form_data["publish_date"] = self.post.publish_date if self.post else datetime.utcnow()
        form_data.pop("publish_time", None)

        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, post_id)
            if post_to_update and post_to_update.userinfo_id == int(self.my_userinfo_id):
                for key, value in form_data.items():
                    setattr(post_to_update, key, value)
                session.add(post_to_update)
                session.commit()
        
        return rx.redirect(f"/blog/{post_id}")


# --- ESTADO PARA LA PÁGINA PÚBLICA (BLOG Y COMENTARIOS) ---

class CommentState(SessionState):
    """Estado que maneja tanto la vista del post público como sus comentarios."""
    post: Optional[BlogPostModel] = None
    img_idx: int = 0
    comments: list[CommentModel] = []
    new_comment_text: str = ""

    @rx.var
    def post_id(self) -> str:
        return self.router.page.params.get("blog_public_id", "")
        
    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.var
    def content(self) -> str:
        if self.post and self.post.content:
            return self.post.content
        return ""

    @rx.event
    def on_load(self):
        """Carga el post Y los comentarios."""
        # Limpiar el estado anterior
        self.post = None
        self.comments = []
        
        try:
            pid = int(self.post_id)
        except (ValueError, TypeError):
            return

        with rx.session() as session:
            # Cargar el post
            self.post = session.exec(
                select(BlogPostModel).where(
                    BlogPostModel.id == pid,
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.utcnow()
                )
            ).one_or_none()
            
            # Si el post se encontró, cargar sus comentarios
            if self.post:
                statement = (
                    select(CommentModel)
                    .options(
                        sqlalchemy.orm.joinedload(CommentModel.userinfo).joinedload(UserInfo.user),
                        sqlalchemy.orm.joinedload(CommentModel.votes)
                    )
                    .where(CommentModel.blog_post_id == self.post.id)
                    .order_by(CommentModel.created_at.desc())
                )
                self.comments = session.exec(statement).unique().all()
        
        self.img_idx = 0

    @rx.var
    def user_can_comment(self) -> bool:
        if not self.is_authenticated or not self.post:
            return False
        with rx.session() as session:
            purchase_record = session.exec(
                select(PurchaseModel).where(
                    PurchaseModel.userinfo_id == self.authenticated_user_info.id,
                    PurchaseModel.status == PurchaseStatus.CONFIRMED,
                    PurchaseModel.items.any(PurchaseItemModel.blog_post_id == self.post.id)
                )
            ).first()
            return purchase_record is not None
            
    # (Los métodos add_comment, handle_vote y de imágenes pueden permanecer como estaban)