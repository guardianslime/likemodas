# likemodas/blog/state.py (VERSIÓN CORREGIDA Y FINAL)

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

    # --- 👇 INICIO DE LA CORRECCIÓN: Se restauran estas variables ---
    @rx.var
    def formatted_price(self) -> str:
        """Devuelve el precio del post formateado como moneda."""
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.var
    def blog_post_edit_url(self) -> str:
        """Devuelve la URL para editar el post actual."""
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"
        return BLOG_POSTS_ROUTE
    # --- FIN DE LA CORRECCIÓN ---

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
            # La lógica del admin no necesita verificar si está publicado
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
        # CORRECCIÓN: Redirigir a la lista de posts del admin
        return rx.redirect(BLOG_POSTS_ROUTE)

class BlogEditFormState(BlogPostState):
    """Estado para el formulario de EDITAR posts."""
    post_content: str = ""
    post_publish_active: bool = False
    price_str: str = "0.0"

    @rx.event
    def on_load_edit(self):
        """Carga los datos del post en el formulario cuando la página de edición carga."""
        self.get_post_detail()
        if self.post:
            self.post_content = self.post.content or ""
            self.post_publish_active = self.post.publish_active
            self.price_str = str(self.post.price or 0.0)

    # --- 👇 FUNCIÓN RESTAURADA Y NECESARIA ---
    @rx.event
    def set_price(self, value: str):
        """Actualiza el precio en el estado desde el input del formulario."""
        self.price_str = value
    # --- FIN DE LA RESTAURACIÓN ---

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
        """Maneja el envío del formulario de edición."""
        post_id = int(form_data.pop("post_id", 0))
        if not post_id or not self.is_admin:
            return rx.toast.error("No se puede guardar el post.")

        # Actualiza los datos del formulario
        form_data["publish_active"] = form_data.get("publish_active") == "on"
        try:
            form_data["price"] = float(self.price_str)
        except ValueError:
            return rx.toast.error("Precio inválido.")
        
        # Manejo de fecha
        if form_data.get("publish_date") and form_data.get("publish_time"):
            try:
                dt_str = f"{form_data['publish_date']} {form_data['publish_time']}"
                form_data["publish_date"] = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                form_data["publish_date"] = self.post.publish_date
        form_data.pop("publish_time", None)

        # Guardar en la base de datos
        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, post_id)
            if post_to_update:
                # Actualiza solo los campos del formulario
                for key, value in form_data.items():
                    setattr(post_to_update, key, value)
                session.add(post_to_update)
                session.commit()
        
        # Redirige a la página de detalle del admin, no a la de edición
        return rx.redirect(f"/blog/{post_id}")

    # (El resto de los métodos de BlogEditFormState pueden permanecer como estaban)


# --- ESTADOS PARA PÁGINAS PÚBLICAS ---

class BlogViewState(SessionState):
    """Estado para la VISTA PÚBLICA de un post."""
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.var
    def post_id(self) -> str:
        return self.router.page.params.get("blog_public_id", "")

    @rx.event
    def on_load(self):
        try:
            pid = int(self.post_id)
        except (ValueError, TypeError):
            self.post = None
            return

        with rx.session() as session:
            self.post = session.exec(
                select(BlogPostModel).where(
                    BlogPostModel.id == pid,
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.utcnow()
                )
            ).one_or_none()
        self.img_idx = 0
    
    # (Los métodos de imagen y las propiedades computadas pueden permanecer como estaban)

class CommentState(BlogViewState):
    """Estado para manejar la sección de comentarios con permisos de compra."""
    
    comments: list[CommentModel] = []
    new_comment_text: str = ""

    # --- 👇 INICIO DE LA CORRECCIÓN: Copiamos las variables aquí ---
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

    @rx.var
    def content(self) -> str:
        if self.post and self.post.content:
            return self.post.content
        return ""

    @rx.var
    def has_post(self) -> bool:
        return self.post is not None
    # --- FIN DE LA CORRECCIÓN ---

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

    def load_comments(self):
        if not self.post:
            self.comments = []
            return
        with rx.session() as session:
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
            
    def on_load(self):
        super().on_load()
        self.load_comments()

    @rx.event
    def add_comment(self, form_data: dict):
        content = form_data.get("comment_text", "").strip()
        if not self.user_can_comment or not self.post or not content:
            return rx.toast.error("No tienes permiso para comentar en este producto.")

        with rx.session() as session:
            comment = CommentModel(
                content=content,
                userinfo_id=self.authenticated_user_info.id,
                blog_post_id=self.post.id
            )
            session.add(comment)
            session.commit()

        self.new_comment_text = ""
        self.load_comments()

    @rx.event
    def handle_vote(self, comment_id: int, vote_type_str: str):
        vote_type = VoteType(vote_type_str)
        if not self.is_authenticated:
            return rx.toast.error("Debes iniciar sesión para votar.")

        with rx.session() as session:
            existing_vote = session.exec(
                select(CommentVoteModel).where(
                    CommentVoteModel.comment_id == comment_id,
                    CommentVoteModel.userinfo_id == self.authenticated_user_info.id
                )
            ).one_or_none()

            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    session.delete(existing_vote)
                else:
                    existing_vote.vote_type = vote_type
                    session.add(existing_vote)
            else:
                new_vote = CommentVoteModel(
                    vote_type=vote_type,
                    userinfo_id=self.authenticated_user_info.id,
                    comment_id=comment_id
                )
                session.add(new_vote)
            
            session.commit()
        
        self.load_comments()