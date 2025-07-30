# likemodas/blog/state.py (VERSIÓN CON HORA EN FORMATO 12 HORAS)

from datetime import datetime
from typing import Optional, List
from typing import Literal
from unittest import result
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState

from ..models import BlogPostModel, UserInfo, CommentModel, CommentVoteModel, VoteType, PurchaseModel, PurchaseItemModel, PurchaseStatus, Category # <-- AÑADIR Category
from ..data.product_options import (
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES
)


BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

# (Las clases BlogPostState y BlogAddFormState no necesitan cambios)
class BlogPostState(SessionState):
    """Estado para la lista y detalle de posts del admin."""
    posts: list[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    img_idx: int = 0
    
    search_query: str = ""
    
    # Esta es la propiedad computada que ya habías añadido, está correcta.

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
        """Devuelve una lista con los valores de las categorías."""
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
        self.img_idx = 0

    @rx.event
    def toggle_publish_status(self, post_id: int):
        if not self.is_admin:
            return rx.toast.error("No tienes permiso para esta acción.")
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post and post.userinfo_id == int(self.my_userinfo_id):
                post.publish_active = not post.publish_active
                
                if post.publish_active:
                    post.publish_date = datetime.utcnow()
                    yield rx.toast.success("¡Publicación activada!")
                else:
                    yield rx.toast.info("Publicación desactivada.")
                
                session.add(post)
                session.commit()
      
        yield type(self).get_post_detail

    @rx.event
    def delete_post(self, post_id: int):
        if not self.is_admin: return
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == int(self.my_userinfo_id):
                session.delete(post_to_delete)
                session.commit()
        return type(self).load_posts
    


class BlogAddFormState(SessionState):
    """Estado para el formulario de AÑADIR posts."""
    title: str = ""
    content: str = ""
    price: float = 0.0
    category: str = ""
    temp_images: list[str] = []

    # Campos para Ropa
    talla: str = ""
    tipo_tela: str = ""
    color_ropa: str = ""
    tipo_prenda: str = ""

    # Campos para Calzado
    numero_calzado: str = ""
    material_calzado: str = ""
    color_calzado: str = ""
    tipo_zapato: str = ""

    # Campos para Mochilas
    material_mochila: str = ""
    medidas: str = ""
    tipo_mochila: str = ""
    
    # --- ✨ NUEVOS ESTADOS PARA BÚSQUEDA EN FORMULARIO ---
    search_add_tipo_prenda: str = ""
    search_add_color_ropa: str = ""
    search_add_talla: str = ""
    search_add_tipo_tela: str = ""
    search_add_tipo_zapato: str = ""
    search_add_color_calzado: str = ""
    search_add_numero_calzado: str = ""
    search_add_material_calzado: str = ""
    search_add_tipo_mochila: str = ""
    search_add_material_mochila: str = ""

    # --- ✨ NUEVOS EVENT HANDLERS PARA BÚSQUEDA ---
    def set_search_add_tipo_prenda(self, query: str): self.search_add_tipo_prenda = query
    def set_search_add_color_ropa(self, query: str): self.search_add_color_ropa = query
    def set_search_add_talla(self, query: str): self.search_add_talla = query
    def set_search_add_tipo_tela(self, query: str): self.search_add_tipo_tela = query
    def set_search_add_tipo_zapato(self, query: str): self.search_add_tipo_zapato = query
    def set_search_add_color_calzado(self, query: str): self.search_add_color_calzado = query
    def set_search_add_numero_calzado(self, query: str): self.search_add_numero_calzado = query
    def set_search_add_material_calzado(self, query: str): self.search_add_material_calzado = query
    def set_search_add_tipo_mochila(self, query: str): self.search_add_tipo_mochila = query
    def set_search_add_material_mochila(self, query: str): self.search_add_material_mochila = query

    # --- ✨ NUEVAS PROPIEDADES COMPUTADAS PARA LISTAS FILTRADAS DEL FORMULARIO ---
    @rx.var
    def filtered_add_colores(self) -> list[str]:
        if not self.search_add_color_ropa.strip(): return LISTA_COLORES
        return [op for op in LISTA_COLORES if self.search_add_color_ropa.lower() in op.lower()]
    
    @rx.var
    def filtered_add_tallas(self) -> list[str]:
        if not self.search_add_talla.strip(): return LISTA_TALLAS_ROPA
        return [op for op in LISTA_TALLAS_ROPA if self.search_add_talla.lower() in op.lower()]

    @rx.var
    def filtered_add_materiales(self) -> list[str]:
        if not self.search_add_tipo_tela.strip(): return LISTA_MATERIALES
        return [op for op in LISTA_MATERIALES if self.search_add_tipo_tela.lower() in op.lower()]

    @rx.var
    def filtered_add_numeros_calzado(self) -> list[str]:
        if not self.search_add_numero_calzado.strip(): return LISTA_NUMEROS_CALZADO
        return [op for op in LISTA_NUMEROS_CALZADO if self.search_add_numero_calzado.lower() in op.lower()]

    def _create_post(self, publish: bool) -> rx.event.EventSpec:
        """Helper method to create and save a post."""
        if not self.is_admin: return rx.window_alert("No tienes permiso.")
        if self.price <= 0: return rx.window_alert("El precio debe ser mayor a cero.")
        if not self.title.strip(): return rx.window_alert("El título no puede estar vacío.")
        if not self.category: return rx.window_alert("Debes seleccionar una categoría.")

        # ... (la lógica para recolectar los atributos es la misma)
        attributes = {}
        if self.category == Category.ROPA.value:
            attributes = {
                "talla": self.talla, "tipo_tela": self.tipo_tela,
                "color": self.color_ropa, "tipo_prenda": self.tipo_prenda,
            }
        elif self.category == Category.CALZADO.value:
            attributes = {
                "numero_calzado": self.numero_calzado, "material": self.material_calzado,
                "color": self.color_calzado, "tipo_zapato": self.tipo_zapato,
            }
        elif self.category == Category.MOCHILAS.value:
            attributes = {
                "material": self.material_mochila, "medidas": self.medidas,
                "tipo_mochila": self.tipo_mochila,
            }

        with rx.session() as session:
            post = BlogPostModel(
                title=self.title.strip(), content=self.content.strip(),
                price=self.price, image_urls=self.temp_images.copy(),
                userinfo_id=self.my_userinfo_id, 
                publish_active=publish,
                publish_date=datetime.utcnow(),
                category=self.category,
                attributes=attributes
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            new_post_id = post.id
        
        self.reset()
        return rx.redirect(f"/blog/{new_post_id}")
    
    @rx.event
    def clear_attribute(self, attribute_name: str):
        """Limpia el valor de un atributo del formulario."""
        if hasattr(self, attribute_name):
            setattr(self, attribute_name, "")
            
            search_attribute_name = f"search_add_{attribute_name}"
            if hasattr(self, search_attribute_name):
                setattr(self, search_attribute_name, "")

    @rx.event
    def clear_all_attributes(self):
        """Limpia todos los atributos y campos de búsqueda del formulario."""
        # Ropa
        self.talla = ""
        self.tipo_tela = ""
        self.color_ropa = ""
        self.tipo_prenda = ""
        # Calzado
        self.numero_calzado = ""
        self.material_calzado = ""
        self.color_calzado = ""
        self.tipo_zapato = ""
        # Mochilas
        self.material_mochila = ""
        self.medidas = ""
        self.tipo_mochila = ""
        # Campos de búsqueda
        self.search_add_tipo_prenda = ""
        self.search_add_color_ropa = ""
        self.search_add_talla = ""
        self.search_add_tipo_tela = ""
        self.search_add_tipo_zapato = ""
        self.search_add_color_calzado = ""
        self.search_add_numero_calzado = ""
        self.search_add_material_calzado = ""
        self.search_add_tipo_mochila = ""
        self.search_add_material_mochila = ""
    
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
        """Este método crea un post pero NO lo publica."""
        return self._create_post(publish=False)

    @rx.event
    def submit_and_publish(self):
        """Este método crea un post y SÍ lo publica."""
        return self._create_post(publish=True)

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
        if self.post and self.post.publish_date:
            return self.post.publish_date.strftime("%Y-%m-%d")
        return ""

    @rx.var
    def publish_display_time(self) -> str:
        if self.post and self.post.publish_date:
            # --- CAMBIO AQUÍ: de %H:%M:%S a %I:%M:%S %p ---
            return self.post.publish_date.strftime("%I:%M:%S %p")
        return ""

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
                # --- CAMBIO AQUÍ: Se ajusta el formato para aceptar AM/PM ---
                form_data["publish_date"] = datetime.strptime(dt_str, "%Y-%m-%d %I:%M:%S %p")
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

# (La clase CommentState no necesita cambios)
class CommentState(SessionState):
    """Estado que maneja tanto la vista del post público como sus comentarios."""
    post: Optional = None
    img_idx: int = 0
    
    # --- ✅ CORRECCIÓN 1: Inicialización de estado mutable ---
    # Se utiliza rx.field(default_factory=list) para la inicialización segura
    # de la lista de comentarios, previniendo el error de estado compartido.
    comments: list[CommentModel] = rx.field(default_factory=list)
    
    new_comment_text: str = ""
    new_comment_rating: int = 0

    # --- (Propiedades @rx.var sin cambios) ---
    @rx.var
    def product_attributes(self) -> list[tuple[str, str]]:
        if not self.post or not self.post.attributes:
            return # Devuelve una lista vacía si no hay post o atributos
        
        # --- ✅ CORRECCIÓN 2: Inicialización de lista local ---
        # Se inicializa una lista vacía para poder añadirle elementos.
        formatted_attrs =
        
        for key, value in self.post.attributes.items():
            if value and str(value).strip():
                formatted_key = key.replace('_', ' ').title()
                formatted_attrs.append((f"{formatted_key}:", str(value)))
                
        return formatted_attrs

    #... (el resto de tus propiedades @rx.var como rating_count, average_rating, etc., van aquí sin cambios)...
    @rx.var
    def rating_count(self) -> int:
        return len(self.comments)

    @rx.var
    def average_rating(self) -> float:
        if not self.comments:
            return 0.0
        total_rating = sum(comment.rating for comment in self.comments)
        return total_rating / len(self.comments)

    @rx.var
    def post_id(self) -> str:
        return self.router.page.params.get("blog_public_id", "")
        
    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    #... (el resto de tus propiedades @rx.var)...

    @rx.event
    def on_load(self):
        """Carga el post y sus comentarios de forma segura y eficiente."""
        self.post = None
        
        # --- ✅ CORRECCIÓN 3: Reseteo de lista ---
        # Al resetear el estado, la lista de comentarios debe ser una lista vacía.
        self.comments =
        
        self.img_idx = 0
        self.new_comment_text = ""
        self.new_comment_rating = 0

        try:
            pid = int(self.post_id)
        except (ValueError, TypeError):
            return

        with rx.session() as session:
            db_post_result = session.exec(
                select(BlogPostModel)
               .options(
                    sqlalchemy.orm.joinedload(BlogPostModel.comments)
                   .joinedload(CommentModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(BlogPostModel.comments)
                   .joinedload(CommentModel.votes)
                )
               .where(
                    BlogPostModel.id == pid,
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.utcnow()
                )
            ).unique().one_or_none()

            if db_post_result:
                self.post = db_post_result
                self.comments = sorted(
                    db_post_result.comments,
                    key=lambda c: c.created_at,
                    reverse=True
                )

    @rx.var
    def content(self) -> str:
        if self.post and self.post.content:
            return self.post.content
        return ""

    @rx.var
    def imagen_actual(self) -> str:
        if self.post and self.post.image_urls and len(self.post.image_urls) > self.img_idx:
            return self.post.image_urls[self.img_idx]
        return ""
    
    @rx.var
    def user_has_purchased(self) -> bool:
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
        return self.user_has_purchased and not self.user_has_commented


    # --- (El resto de tus eventos como add_comment, handle_vote, etc. van aquí sin cambios) ---
    @rx.event
    def set_new_comment_rating(self, rating: int):
        self.new_comment_rating = rating
    
    @rx.event
    def add_comment(self, form_data: dict):
        content = form_data.get("comment_text", "").strip()
        
        if not self.user_can_comment or not self.post or not content:
            return rx.toast.error("No tienes permiso para comentar o el texto está vacío.")
    
        if self.new_comment_rating == 0:
            return rx.toast.error("Por favor, selecciona una calificación de 1 a 5 estrellas.")

        with rx.session() as session:
            comment = CommentModel(
                content=content,
                rating=self.new_comment_rating,
                userinfo_id=self.authenticated_user_info.id,
                blog_post_id=self.post.id
            )
            session.add(comment)
            session.commit()
        
        self.new_comment_text = ""
        self.new_comment_rating = 0
        return self.on_load()

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
        return self.on_load()

    @rx.event
    def siguiente_imagen(self):
        if self.post and self.post.image_urls:
            self.img_idx = (self.img_idx + 1) % len(self.post.image_urls)

    @rx.event
    def anterior_imagen(self):
        if self.post and self.post.image_urls:
            self.img_idx = (self.img_idx - 1 + len(self.post.image_urls)) % len(self.post.image_urls)