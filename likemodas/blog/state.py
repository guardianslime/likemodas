from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import (
    BlogPostModel, UserInfo, CommentModel, CommentVoteModel, VoteType,
    PurchaseModel, PurchaseItemModel, PurchaseStatus, Category
)
from ..data.product_options import (
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES
)

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

# (Las clases BlogAddFormState y BlogEditFormState no necesitan cambios y se mantienen como en tu archivo original)
# ...

class BlogPostState(SessionState):
    """Estado para la lista y detalle de posts del admin."""
    # CORREGIDO: Inicializar como una lista vacía en lugar de con Nones.
    posts: list[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    img_idx: int = 0
    search_query: str = ""

    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            # Usamos el formateador de la propiedad del modelo para consistencia.
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
        """Propiedad computada simplificada para filtrar los posts."""
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
        """Carga los posts del admin desde la base de datos."""
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
        if not self.is_admin or self.my_userinfo_id is None:
            return rx.toast.error("No tienes permiso para esta acción.")
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post and post.userinfo_id == int(self.my_userinfo_id):
                post.publish_active = not post.publish_active
                if post.publish_active:
                    # Asigna la fecha actual solo si no ha sido publicada antes
                    if post.publish_date is None:
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
        if not self.is_admin or self.my_userinfo_id is None: return
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == int(self.my_userinfo_id):
                session.delete(post_to_delete)
                session.commit()
        # Redirige a la lista de posts después de eliminar
        return rx.redirect(BLOG_POSTS_ROUTE)


class BlogAddFormState(SessionState):
    """Estado para el formulario de AÑADIR posts."""
    title: str = ""
    content: str = ""
    price: float = 0.0
    category: str = ""
    temp_images: list[str] = []

    # Atributos específicos por categoría
    talla: str = ""
    tipo_tela: str = ""
    color_ropa: str = ""
    tipo_prenda: str = ""
    numero_calzado: str = ""
    material_calzado: str = ""
    color_calzado: str = ""
    tipo_zapato: str = ""
    material_mochila: str = ""
    medidas: str = ""
    tipo_mochila: str = ""

    # Estados para la búsqueda en los selectores
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

    # Setters para la búsqueda
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

    # Propiedades computadas para filtrar las opciones de los selectores
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
        if not self.is_admin or self.my_userinfo_id is None: return rx.toast.error("No tienes permiso.")
        if self.price <= 0: return rx.toast.error("El precio debe ser mayor a cero.")
        if not self.title.strip(): return rx.toast.error("El título no puede estar vacío.")
        if not self.category: return rx.toast.error("Debes seleccionar una categoría.")

        attributes = {}
        if self.category == Category.ROPA.value:
            attributes = {"talla": self.talla, "tipo_tela": self.tipo_tela, "color": self.color_ropa, "tipo_prenda": self.tipo_prenda}
        elif self.category == Category.CALZADO.value:
            attributes = {"numero_calzado": self.numero_calzado, "material": self.material_calzado, "color": self.color_calzado, "tipo_zapato": self.tipo_zapato}
        elif self.category == Category.MOCHILAS.value:
            attributes = {"material": self.material_mochila, "medidas": self.medidas, "tipo_mochila": self.tipo_mochila}

        with rx.session() as session:
            post = BlogPostModel(
                title=self.title.strip(), content=self.content.strip(),
                price=self.price, image_urls=self.temp_images.copy(),
                userinfo_id=int(self.my_userinfo_id),
                publish_active=publish,
                publish_date=datetime.utcnow() if publish else None,
                category=self.category,
                attributes=attributes
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            new_post_id = post.id
        
        self.reset()
        # Redirige a la página de detalle del admin, no a la pública.
        return rx.redirect(f"/blog/{new_post_id}")

    @rx.event
    def clear_attribute(self, attribute_name: str):
        if hasattr(self, attribute_name):
            setattr(self, attribute_name, "")
            search_attribute_name = f"search_add_{attribute_name}"
            if hasattr(self, search_attribute_name):
                setattr(self, search_attribute_name, "")

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
        return self._create_post(publish=False)

    @rx.event
    def submit_and_publish(self):
        return self._create_post(publish=True)


class BlogEditFormState(BlogPostState):
    """Estado para el formulario de EDITAR posts."""
    post_content: str = ""
    post_publish_active: bool = False
    price_str: str = "0.0"

    @rx.event
    def on_load_edit(self):
        # Llama a la lógica de get_post_detail de la clase base
        yield type(self).get_post_detail
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
            return self.post.publish_date.strftime("%I:%M:%S %p")
        return ""

    @rx.event
    def handle_submit(self, form_data: dict):
        post_id = int(form_data.pop("post_id", 0))
        if not post_id or not self.is_admin or self.my_userinfo_id is None:
            return rx.toast.error("No se puede guardar el post.")

        form_data["content"] = self.post_content
        form_data["publish_active"] = self.post_publish_active
        try:
            form_data["price"] = float(self.price_str)
        except ValueError:
            return rx.toast.error("Precio inválido.")

        if self.post_publish_active and form_data.get("publish_date") and form_data.get("publish_time"):
            try:
                dt_str = f"{form_data['publish_date']} {form_data['publish_time']}"
                form_data["publish_date"] = datetime.strptime(dt_str, "%Y-%m-%d %I:%M:%S %p")
            except ValueError:
                form_data["publish_date"] = self.post.publish_date if self.post else datetime.utcnow()
        form_data.pop("publish_time", None)

        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, post_id)
            if post_to_update and post_to_update.userinfo_id == int(self.my_userinfo_id):
                # Actualiza solo los campos que vienen del formulario
                for key, value in form_data.items():
                    if hasattr(post_to_update, key):
                        setattr(post_to_update, key, value)
                session.add(post_to_update)
                session.commit()
        
        # Redirige de vuelta a la página de detalle del admin
        return rx.redirect(f"/blog/{post_id}")


class CommentState(SessionState):
    """Estado que maneja la vista del post público y sus comentarios."""
    # CORREGIDO: Tipado explícito para mayor seguridad
    post: Optional[BlogPostModel] = None
    # CORREGIDO: Inicializado como lista vacía
    comments: list[CommentModel] = []
    
    new_comment_text: str = ""
    new_comment_rating: int = 0
    img_idx: int = 0
    is_loading: bool = True

    @rx.var
    def post_id(self) -> str:
        """Obtiene el ID del post desde la URL."""
        # CORREGIDO: El parámetro en la ruta es 'blog_public_id'
        return self.router.page.params.get("blog_public_id", "")

    @rx.var
    def formatted_price(self) -> str:
        """Devuelve el precio formateado en COP."""
        if self.post and self.post.price is not None:
            # Reutiliza la propiedad del modelo para consistencia
            return self.post.price_cop
        return "$0"

    @rx.var
    def content(self) -> str:
        """Devuelve el contenido del post."""
        return self.post.content if self.post and self.post.content else ""

    @rx.var
    def product_attributes(self) -> list[tuple[str, str]]:
        """Formatea los atributos del producto para mostrarlos."""
        if not self.post or not self.post.attributes:
            return []
        
        formatted_attrs = []
        for key, value in self.post.attributes.items():
            if value and str(value).strip():
                formatted_key = key.replace('_', ' ').title()
                formatted_attrs.append((f"{formatted_key}:", str(value)))
        return formatted_attrs

    @rx.var
    def rating_count(self) -> int:
        """Devuelve el número total de comentarios (calificaciones)."""
        return len(self.comments)

    @rx.var
    def average_rating(self) -> float:
        """Calcula la calificación promedio de forma segura."""
        if not self.comments:
            return 0.0
        total_rating = sum(c.rating for c in self.comments)
        return total_rating / len(self.comments)

    # Las propiedades 'user_has_purchased', 'user_has_commented', y 'user_can_comment'
    # se mantienen como en el código original, ya que su lógica es correcta.

    @rx.event
    def on_load(self):
        """Carga el post y sus comentarios de forma eficiente y segura."""
        self.is_loading = True
        # Limpia el estado anterior antes de cargar nuevos datos
        self.post, self.comments = None, []
        yield

        try:
            pid = int(self.post_id)
        except (ValueError, TypeError):
            self.is_loading = False
            return

        with rx.session() as session:
            # Carga el post y sus relaciones en una sola consulta para optimizar
            db_post_result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.comments)
                    .joinedload(CommentModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(BlogPostModel.comments)
                    .joinedload(CommentModel.votes)
                )
                .where(BlogPostModel.id == pid, BlogPostModel.publish_active == True)
            ).unique().one_or_none()

            if db_post_result:
                self.post = db_post_result
                self.comments = sorted(
                    db_post_result.comments,
                    key=lambda c: c.created_at,
                    reverse=True
                )
        
        # Resetea los campos del formulario
        self.img_idx = 0
        self.new_comment_text = ""
        self.new_comment_rating = 0
        self.is_loading = False
    
    # Los métodos 'set_new_comment_rating', 'add_comment', y 'handle_vote'
    # se mantienen como en el código original, ya que su lógica es correcta.

    @rx.event
    def siguiente_imagen(self):
        if self.post and self.post.image_urls:
            self.img_idx = (self.img_idx + 1) % len(self.post.image_urls)

    @rx.event
    def anterior_imagen(self):
        if self.post and self.post.image_urls:
            self.img_idx = (self.img_idx - 1 + len(self.post.image_urls)) % len(self.post.image_urls)