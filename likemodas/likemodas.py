# likemodas/likemodas.py (CORREGIDO)

import reflex as rx
from likemodas.state import AppState
from likemodas.components.base import base_page  # <--- Importa el layout base
from likemodas.pages.index import index_page
from likemodas.pages.product import product_page
from likemodas.pages.admin import admin_page

# Crea la instancia de la aplicación
app = rx.App()

# Añade las páginas, envolviendo cada una con el layout base
app.add_page(base_page(index_page()), route="/", on_load=AppState.load_products)
app.add_page(base_page(product_page()), route="/product/[product_id]", on_load=AppState.load_product_detail)
app.add_page(base_page(admin_page()), route="/admin")

# Ya no se necesita la línea app.add_component()