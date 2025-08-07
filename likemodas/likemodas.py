# likemodas/likemodas.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
from likemodas.state import AppState, ProductDetailState # <--- Importamos ambos estados
from likemodas.components.base import base_page
from likemodas.pages.index import index_page
from likemodas.pages.product import product_page
from likemodas.pages.admin import admin_page

app = rx.App()

app.add_page(base_page(index_page()), route="/", on_load=AppState.load_products)
app.add_page(base_page(admin_page()), route="/admin")

# ✨ EXPLICACIÓN: La página de producto ahora usa ProductDetailState y su método de carga.
app.add_page(
    base_page(product_page()),
    route="/product/[product_id]",
    on_load=ProductDetailState.load_product_detail
)