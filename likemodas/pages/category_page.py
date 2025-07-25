import reflex as rx
from ..ui.base import base_page
from ..auth.state import SessionState
from ..cart.state import CartState, ProductCardData
# --- 👇 CAMBIO 1: Importa los dos componentes ---
from ..ui.components import product_gallery_component, categories_button
from ..models import BlogPostModel, Category
from sqlmodel import select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import cast
from sqlalchemy import String, cast
from datetime import datetime
import sqlalchemy
from ..ui.filter_panel import floating_filter_panel

class CategoryPageState(SessionState):
    posts_in_category: list[ProductCardData] = []


    @rx.event
    def load_category_posts(self):
        self.current_category = self.router.page.params.get("cat_name", "todos")
        
        with rx.session() as session:
            query_filter = [
                BlogPostModel.publish_active == True, 
                BlogPostModel.publish_date < datetime.now()
            ]
            if self.current_category != "todos":
                try:
                    category_enum = Category(self.current_category)
                    query_filter.append(BlogPostModel.category == category_enum)
                except ValueError:
                    self.posts_in_category = []
                    return

            statement = (
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(*query_filter)
                .order_by(BlogPostModel.created_at.desc())
            )
            results = session.exec(statement).unique().all()
            self.posts_in_category = [
                ProductCardData(
                    id=p.id,
                    title=p.title,
                    price=p.price,
                    images=p.images,
                    average_rating=p.average_rating,
                    rating_count=p.rating_count,
                    # --- ✨ ASEGÚRATE DE QUE ESTA LÍNEA EXISTA ---
                    attributes=p.attributes
                ) for p in results
            ]
    
    @rx.var
    def filtered_posts_in_category(self) -> list[ProductCardData]:
        """Filters posts in the current category by price and dynamic attributes."""
        posts_to_filter = self.posts_in_category
        
        # --- Price Filter (existing logic) ---
        try:
            min_p = float(self.min_price) if self.min_price else 0
        except ValueError: min_p = 0
        try:
            max_p = float(self.max_price) if self.max_price else float('inf')
        except ValueError: max_p = float('inf')

        if min_p > 0 or max_p != float('inf'):
            posts_to_filter = [p for p in posts_to_filter if (p.price >= min_p and p.price <= max_p)]

        # --- ✨ NEW DYNAMIC ATTRIBUTE FILTERING ---
        with rx.session() as session:
            post_ids = [p.id for p in posts_to_filter]
            if not post_ids:
                return []

            query = select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))

            # Apply filters based on the current category
            category_from_url = self.current_category
            if category_from_url == Category.ROPA.value:
                if self.filter_color:
                    query = query.where(cast(BlogPostModel.attributes['color'], String).ilike(f"%{self.filter_color}%"))
                if self.filter_talla:
                    query = query.where(cast(BlogPostModel.attributes['talla'], String).ilike(f"%{self.filter_talla}%"))
                if self.filter_tipo_prenda:
                    query = query.where(cast(BlogPostModel.attributes['tipo_prenda'], String) == self.filter_tipo_prenda)
            
            elif category_from_url == Category.CALZADO.value:
                if self.filter_color:
                    query = query.where(cast(BlogPostModel.attributes['color'], String).ilike(f"%{self.filter_color}%"))
                if self.filter_numero_calzado:
                    query = query.where(cast(BlogPostModel.attributes['numero_calzado'], String) == self.filter_numero_calzado)
                if self.filter_tipo_zapato:
                    query = query.where(cast(BlogPostModel.attributes['tipo_zapato'], String) == self.filter_tipo_zapato)
            
            elif category_from_url == Category.MOCHILAS.value:
                if self.filter_tipo_mochila:
                    query = query.where(cast(BlogPostModel.attributes['tipo_mochila'], String) == self.filter_tipo_mochila)

            # Execute the final query and return the data
            filtered_db_posts = session.exec(query).all()
            filtered_ids = {p.id for p in filtered_db_posts}
            
            return [p for p in posts_to_filter if p.id in filtered_ids]
        
    # --- 👇 PEGA ESTE BLOQUE DE CÓDIGO COMPLETO AQUÍ 👇 ---
    @rx.var
    def available_colors(self) -> list[dict]:
        """Genera la lista de colores únicos para los productos de esta categoría."""
        from ..utils.helpers import get_unique_options_from_attributes
        return get_unique_options_from_attributes(self.posts_in_category, ["color"])

    @rx.var
    def available_tallas(self) -> list[dict]:
        """Genera la lista de tallas únicas para los productos de esta categoría."""
        from ..utils.helpers import get_unique_options_from_attributes
        return get_unique_options_from_attributes(self.posts_in_category, ["talla"])
    
    @rx.var
    def available_numeros(self) -> list[dict]:
        """Genera la lista de números de calzado únicos para los productos de esta categoría."""
        from ..utils.helpers import get_unique_options_from_attributes
        return get_unique_options_from_attributes(self.posts_in_category, ["numero_calzado"])
    # --- FIN DEL BLOQUE A PEGAR ---


    # --- ✨ MÉTODOS MOVIDOS Y CORREGIDOS AQUÍ 👇 ---
    @rx.var
    def filtered_available_colors(self) -> list[dict]:
        # Corrección: Ahora usa 'self' para acceder a sus propias propiedades
        return self._filter_options(self.available_colors, self.color_search)

    @rx.var
    def filtered_available_tallas(self) -> list[dict]:
        # Corrección: Ahora usa 'self' para acceder a sus propias propiedades
        return self._filter_options(self.available_tallas, self.talla_search)

    @rx.var
    def filtered_available_numeros(self) -> list[dict]:
        # Corrección: Ahora usa 'self' para acceder a sus propias propiedades
        return self._filter_options(self.available_numeros, self.numero_calzado_search)

    
    

# --- ✨ CÓDIGO CORREGIDO PARA LA PÁGINA DE CATEGORÍA --- ✨
def category_page() -> rx.Component:
    # --- 👇 CAMBIO 2: Creamos una variable para el contenido de la página ---
    page_content = rx.center(
        rx.vstack(
            # Se añade el botón de categorías y el panel de filtros condicionalmente
            rx.cond(
                SessionState.is_hydrated,
                rx.cond(
                    ~SessionState.is_admin,
                    rx.fragment(
                        floating_filter_panel(),
                        categories_button()
                    )
                )
            ),
            rx.heading(CategoryPageState.current_category.title(), size="8"),
            rx.cond(
                CategoryPageState.filtered_posts_in_category,
                product_gallery_component(posts=CategoryPageState.filtered_posts_in_category),
                rx.center(
                    rx.text(f"😔 No hay productos en la categoría '{CategoryPageState.current_category}'."),
                    min_height="40vh"
                )
            ),
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )
    
    # --- 👇 CAMBIO 3: Usamos 'public_layout' directamente, igual que las otras páginas públicas ---
    return base_page(page_content)