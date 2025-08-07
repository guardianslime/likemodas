# likemodas/state.py (CORREGIDO)

import reflex as rx
from sqlmodel import Field, Column, JSON
from typing import List, Dict, Optional
import asyncio

class Product(rx.Model, table=True):
    title: str
    content: str
    price: float = 0.0
    image_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_published: bool = Field(default=False)

class AppState(rx.State):
    # ... (código de AppState sin cambios) ...
    products: list[Product] = []
    cart: Dict[int, int] = {}
    temp_images: list[str] = []
    is_uploading: bool = False

    @rx.event
    def load_products(self):
        with rx.session() as session:
            self.products = session.query(Product).where(Product.is_published == True).all()

    @rx.var
    def cart_items_count(self) -> int:
        return sum(self.cart.values())

    @rx.event
    def add_to_cart(self, product_id: int):
        if product_id not in self.cart:
            self.cart[product_id] = 0
        self.cart[product_id] += 1
        return rx.toast.info(f"Producto añadido al carrito. Total: {self.cart[product_id]}")

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.temp_images.append(file.name)
        self.is_uploading = False

    def remove_temp_image(self, filename: str):
        self.temp_images.remove(filename)

    @rx.event
    def create_product(self, form_data: dict):
        title, content, price = form_data.get("title"), form_data.get("content"), form_data.get("price")
        if not all([title, content, price, self.temp_images]):
            return rx.toast.error("Todos los campos y al menos una imagen son requeridos.")
        with rx.session() as session:
            new_product = Product(title=title, content=content, price=float(price), image_urls=self.temp_images, is_published=True)
            session.add(new_product)
            session.commit()
        self.temp_images = []
        yield rx.toast.success("¡Producto creado con éxito!")
        return rx.set_value("form-create-product", "")


class ProductDetailState(AppState):
    product_detail: Optional[Product] = None
    is_loading: bool = True

    # ▼▼▼ ESTA ES LA FUNCIÓN CORREGIDA ▼▼▼
    @rx.event
    async def load_product_detail(self):
        self.is_loading = True
        with rx.session() as session:
            # Reflex poblará self.product_id automáticamente
            self.product_detail = session.get(Product, int(self.product_id))
        # Se cambia 'yield' por 'await' para la operación asíncrona
        await asyncio.sleep(0.05)
        self.is_loading = False