# likemodas/blog/state.py (VERSIÓN ACTUALIZADA)

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, CommentModel, CommentVoteModel, VoteType, PurchaseModel, PurchaseItemModel, PurchaseStatus

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

# --- ESTADOS PARA PÁGINAS DE ADMINISTRACIÓN (No cambian) ---

class BlogPostState(SessionState):
    """Estado para la lista y detalle de posts del admin."""
    posts: list[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    img_idx: int = 0
    # ... (el resto del código de BlogPostState no cambia)
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
    def toggle_publish_status(self, post_id: int):
        """Cambia el estado de publicación de un post y actualiza la fecha."""
        if not self.is_admin:
            return rx.toast.error("No tienes permiso para esta acción.")
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post and post.userinfo_id == int(self.my_userinfo_id):
                # Cambia el estado de publicación
                post.publish_active = not post.publish_active
                
                # Si se está publicando, actualiza la fecha de publicación a la actual
                if post.publish_active:
                    post.publish_date = datetime.utcnow()
                    yield rx.toast.success("¡Publicación activada!")
                else:
                    yield rx.toast.info("Publicación desactivada.")
                
                session.add(post)
                session.commit()
        
        # Recarga los detalles del post para actualizar la UI
        yield type(self).get_post_detail

    @rx.event
    def delete_post(self, post_id: int):
        if not self.is_admin: return
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == int(self.my_userinfo_id):
                session.delete(post_to_delete)
                session.commit()
        return type(self).load_posts # <<< LÍNEA CORREGIDA

class BlogAddFormState(SessionState):
    """Estado para el formulario de AÑADIR posts."""
    title: str = ""
    content: str = ""
    price: float = 0.0
    temp_images: list[str] = []
    # ... (el resto del código de BlogAddFormState no cambia)
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
    # ... (el resto del código de BlogEditFormState no cambia)
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
# --- ✨ CAMBIOS PRINCIPALES AQUÍ ✨ ---
class CommentState(SessionState):
    """Estado que maneja tanto la vista del post público como sus comentarios."""
    post: Optional[BlogPostModel] = None
    img_idx: int = 0
    comments: list[CommentModel] = []
    new_comment_text: str = ""
    
    # ✨ 1. CAMBIO: Se añade estado para la calificación
    new_comment_rating: int = 0

    # --- Variables Computadas (Propiedades) ---
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

    @rx.var
    def imagen_actual(self) -> str:
        if self.post and self.post.images and len(self.post.images) > self.img_idx:
            return self.post.images[self.img_idx]
        return ""
    
    # ✨ 2. CAMBIO: Se divide la lógica de 'user_can_comment' en dos partes para más claridad

    @rx.var
    def user_has_purchased(self) -> bool:
        """Verifica si el usuario ha comprado este producto."""
        if not self.is_authenticated or not self.post or not self.authenticated_user_info:
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

    @rx.var
    def user_has_commented(self) -> bool:
        """Verifica si el usuario ya ha comentado en este producto."""
        if not self.is_authenticated or not self.post or not self.authenticated_user_info:
            return False
        with rx.session() as session:
            existing_comment = session.exec(
                select(CommentModel).where(
                    CommentModel.userinfo_id == self.authenticated_user_info.id,
                    CommentModel.blog_post_id == self.post.id
                )
            ).first()
            return existing_comment is not None

    @rx.var
    def user_can_comment(self) -> bool:
        """Determina si el formulario de comentario debe mostrarse."""
        return self.user_has_purchased and not self.user_has_commented

    # --- Event Handlers (Métodos de Lógica) ---
    @rx.event
    def on_load(self):
        """Carga el post Y los comentarios al entrar a la página."""
        self.post = None
        self.comments = []
        try:
            pid = int(self.post_id)
        except (ValueError, TypeError):
            return

        with rx.session() as session:
            # Cargar el post
            self.post = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(
                    BlogPostModel.id == pid,
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.utcnow()
                )
            ).unique().one_or_none() # <<< SE AÑADIÓ .unique() AQUÍ
            
            # Si el post se encontró, cargar sus comentarios (esta parte ya estaba bien)
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
                self.comments = session.exec(statement).unique().all() [cite: 757]
        
        self.img_idx = 0 
        self.new_comment_text = "" 
        self.new_comment_rating = 0 
    
    # ✨ 3. CAMBIO: Nuevo método para establecer la calificación desde la UI
    @rx.event
    def set_new_comment_rating(self, rating: int):
        """Actualiza la calificación seleccionada por el usuario."""
        self.new_comment_rating = rating
    
    # ✨ 4. CAMBIO: Se actualiza 'add_comment' para guardar la calificación
    @rx.event
    def add_comment(self, form_data: dict):
        """Añade un nuevo comentario con calificación a la base de datos."""
        content = form_data.get("comment_text", "").strip()
        
        if not self.user_can_comment or not self.post or not content:
            return rx.toast.error("No tienes permiso para comentar o el texto está vacío.")
        
        if self.new_comment_rating == 0:
            return rx.toast.error("Por favor, selecciona una calificación de 1 a 5 estrellas.")

        with rx.session() as session:
            comment = CommentModel(
                content=content,
                rating=self.new_comment_rating, # Se guarda la calificación
                userinfo_id=self.authenticated_user_info.id,
                blog_post_id=self.post.id
            )
            session.add(comment)
            session.commit()
        
        # Resetea los campos y recarga todo para mostrar el nuevo comentario
        self.new_comment_text = ""
        self.new_comment_rating = 0
        return self.on_load()

    # (El resto de los métodos como handle_vote, siguiente_imagen, etc., no cambian)
    @rx.event
    def handle_vote(self, comment_id: int, vote_type_str: str):
        """Gestiona un voto (like/dislike) en un comentario."""
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
        return self.on_load()

    @rx.event
    def siguiente_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx + 1) % len(self.post.images)

    @rx.event
    def anterior_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx - 1 + len(self.post.images)) % len(self.post.images)