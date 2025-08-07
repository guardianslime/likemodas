# likemodas/likemodas.py

import reflex as rx
from likemodas.state import AppState
from likemodas.pages.index import index_page
from likemodas.pages.product import product_page
from likemodas.pages.admin import admin_page

# Crea la instancia de la aplicación
app = rx.App(state=AppState)

# Añade las páginas y sus rutas
app.add_page(index_page, route="/", on_load=AppState.load_products)
app.add_page(product_page, route="/product/[product_id]", on_load=AppState.load_product_detail)
app.add_page(admin_page, route="/admin")