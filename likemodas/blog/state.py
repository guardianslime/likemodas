# likemodas/blog/state.py

from datetime import datetime
from typing import Optional
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, CommentModel, CommentVoteModel, VoteType # 👈 Modificar esta importación

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

# ───────────────────────────────
# Estado privado (mis publicaciones)
# ───────────────────────────────

class BlogPostState(SessionState):
    posts: list[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    # --- ✨ NUEVOS MÉTODOS Y VARS AÑADIDOS ✨ ---
    @rx.var
    def imagen_actual(self) -> str:
        """Devuelve la URL de la imagen actual para el carrusel."""
        if self.post and self.post.images and len(self.post.images) > self.img_idx:
            return self.post.images[self.img_idx]
        return ""

    @rx.var
    def formatted_price(self) -> str:
        """Devuelve el precio del post formateado como moneda."""
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.event
    def siguiente_imagen(self):
        """Avanza a la siguiente imagen en el carrusel."""
        if self.post and self.post.images:
            self.img_idx = (self.img_idx + 1) % len(self.post.images)

    @rx.event
    def anterior_imagen(self):
        """Retrocede a la imagen anterior en el carrusel."""
        if self.post and self.post.images:
            self.img_idx = (self.img_idx - 1 + len(self.post.images)) % len(self.post.images)
    # --- FIN DE CAMBIOS ---

    @rx.event
    def delete_post(self, post_id: int):
        """Elimina una publicación de la base de datos y recarga la lista."""
        if self.my_userinfo_id is None:
            return rx.window_alert("No estás autenticado.")
        
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            
            if post_to_delete and post_to_delete.userinfo_id == int(self.my_userinfo_id):
                session.delete(post_to_delete)
                session.commit()
            else:
                return rx.window_alert("No tienes permiso para eliminar esta publicación o no fue encontrada.")
                     
        return self.load_posts

    @rx.event
    def load_posts(self):
        if self.my_userinfo_id is None:
            self.posts = []
            return
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo))
                .where(BlogPostModel.userinfo_id == int(self.my_userinfo_id))
                .order_by(BlogPostModel.created_at.desc())
            ).all()

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_edit_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"
        return BLOG_POSTS_ROUTE

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None
            return
        try:
            post_id_int = int(self.blog_post_id)
        except (ValueError, TypeError):
            self.post = None
            return

        with rx.session() as session:
            self.post = session.exec(
                select(BlogPostModel)
                .options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                    .joinedload(UserInfo.user)
                )
                .where(
                    (BlogPostModel.userinfo_id == int(self.my_userinfo_id)) &
                    (BlogPostModel.id == post_id_int)
                )
            ).one_or_none()
        # Reiniciamos el índice de la imagen al cargar un nuevo post
        self.img_idx = 0

# ───────────────────────────────
# Estado para vista pública
# ───────────────────────────────

class BlogPublicState(SessionState):
    posts: list[BlogPostModel] = []

    def on_load(self):
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .where(BlogPostModel.publish_active == True)
                .order_by(BlogPostModel.created_at.desc())
            ).all()



# ───────────────────────────────
# Estado para añadir publicaciones
# ───────────────────────────────

class BlogAddFormState(SessionState):
    title: str = ""
    content: str = ""
    price: str = ""
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
    def set_price(self, value: str):
        self.price = value

    @rx.event
    def submit(self):
        if self.my_userinfo_id is None:
            return rx.window_alert("Inicia sesión.")

        try:
            parsed_price = float(self.price)
        except ValueError:
            return rx.window_alert("Precio inválido.")

        with rx.session() as session:
            post = BlogPostModel(
                title=self.title.strip(),
                content=self.content.strip(),
                price=parsed_price,
                images=self.temp_images.copy(),
                userinfo_id=self.my_userinfo_id,
                publish_active=True,
                publish_date=datetime.now()
            )
            session.add(post)
            session.commit()
            session.refresh(post)

        self.temp_images = []
        self.title = ""
        self.content = ""
        self.price = ""
        return rx.redirect("/blog/page")

    @rx.event
    def set_price_from_input(self, value: str):
        try:
            self.price = float(value)
        except ValueError:
            self.price = 0.0

class BlogEditFormState(BlogPostState):
    post_content: str = ""
    post_publish_active: bool = False

    def on_load_edit(self):
        self.get_post_detail()
        if self.post:
            self.post_content = self.post.content or ""
            self.post_publish_active = self.post.publish_active

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

    price_str: str = "0.0"

    @rx.event
    def set_price(self, value: str):
        self.price_str = value

    def handle_submit(self, form_data: dict):
        post_id = int(form_data.pop("post_id", 0))

        # Parsear fecha/hora
        final_publish_date = None
        if form_data.get("publish_date") and form_data.get("publish_time"):
            try:
                dt_str = f"{form_data['publish_date']} {form_data['publish_time']}"
                final_publish_date = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        # Validar precio
        try:
            form_data["price"] = float(self.price_str)
        except ValueError:
            return rx.window_alert("Precio inválido.")

        form_data["publish_active"] = form_data.get("publish_active") == "on"
        form_data["publish_date"] = final_publish_date
        form_data.pop("publish_time", None)

        self._save_post_edits_to_db(post_id, form_data)
        return rx.redirect(self.blog_post_url)


class BlogViewState(SessionState):
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.var
    def post_id(self) -> str:
        # ✅ Código mejorado para obtener el ID de forma segura
        return self.router.page.params.get("blog_public_id", "")

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

    @rx.event
    def on_load(self):
        try:
            pid = int(self.post_id)
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

class CommentState(BlogViewState):
    """Estado para manejar la sección de comentarios."""
    
    comments: list[CommentModel] = []
    new_comment_text: str = ""

    def load_comments(self):
        """Carga los comentarios para la publicación actual."""
        if not self.post:
            self.comments = []
            return
        with rx.session() as session:
            # Usamos 'unique()' para evitar duplicados por los 'joinedload'
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
            
    # Sobrescribimos on_load para que cargue el post Y los comentarios
    def on_load(self):
        super().on_load() # Llama al on_load del padre (BlogViewState)
        self.load_comments()

    @rx.event
    def add_comment(self, form_data: dict):
        """Añade un nuevo comentario a la base de datos."""
        content = form_data.get("comment_text", "").strip()
        if not self.is_authenticated or not self.post or not content:
            if not self.is_authenticated:
                return rx.toast.error("Debes iniciar sesión para comentar.")
            return

        with rx.session() as session:
            comment = CommentModel(
                content=content,
                userinfo_id=self.authenticated_user_info.id,
                blog_post_id=self.post.id
            )
            session.add(comment)
            session.commit()

        self.new_comment_text = "" # Limpiar el campo de texto
        # Recargar los comentarios para que el nuevo aparezca
        self.load_comments()

    @rx.event
    def handle_vote(self, comment_id: int, vote_type_str: str):
        """Gestiona un voto (like/dislike) en un comentario."""
        vote_type = VoteType(vote_type_str)
        if not self.is_authenticated:
            return rx.toast.error("Debes iniciar sesión para votar.")

        with rx.session() as session:
            # Buscar si el usuario ya votó en este comentario
            existing_vote = session.exec(
                select(CommentVoteModel).where(
                    CommentVoteModel.comment_id == comment_id,
                    CommentVoteModel.userinfo_id == self.authenticated_user_info.id
                )
            ).one_or_none()

            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # Si vota lo mismo, se elimina el voto (toggle off)
                    session.delete(existing_vote)
                else:
                    # Si cambia el voto, se actualiza
                    existing_vote.vote_type = vote_type
                    session.add(existing_vote)
            else:
                # Si no hay voto previo, se crea uno nuevo
                new_vote = CommentVoteModel(
                    vote_type=vote_type,
                    userinfo_id=self.authenticated_user_info.id,
                    comment_id=comment_id
                )
                session.add(new_vote)
            
            session.commit()
        
        # Recargar comentarios para actualizar los contadores
        self.load_comments()