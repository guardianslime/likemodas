# likemodas/state.py (CORREGIDO)

import reflex as rx
from sqlmodel import Field, Column, JSON
from typing import List, Dict, Optional
import asyncio

# ... (El modelo Product no cambia) ...
class Product(rx.Model, table=True):
    title: str
    content: str
    price: float = 0.0
    image_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_published: bool = Field(default=False)

# --- ESTADO PRINCIPAL DE LA APP ---
class AppState(rx.State):
    """Estado único y simple de la aplicación."""

    # ... (El resto del estado no cambia) ...
    products: list[Product] = []
    product_detail: Optional[Product] = None
    cart: Dict[int, int] = {}
    temp_images: list[str] = []
    is_uploading: bool = False

    # ▼▼▼ ESTA ES LA FUNCIÓN CORREGIDA ▼▼▼
    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de imágenes y las guarda temporalmente."""
        self.is_uploading = True
        for file in files:
            upload_data = await file.read()
            # Usamos file.name en lugar de file.filename
            outfile = rx.get_upload_dir() / file.name

            # Guardamos el archivo
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)

            # Actualizamos la lista de imágenes temporales
            self.temp_images.append(file.name)
        self.is_uploading = False

    def remove_temp_image(self, filename: str):
        """Elimina una imagen de la lista temporal."""
        self.temp_images.remove(filename)

    @rx.event
    def create_product(self, form_data: dict):
        """Crea y guarda un nuevo producto en la base de datos."""
        title = form_data.get("title")
        content = form_data.get("content")
        price = form_data.get("price")

        if not all([title, content, price, self.temp_images]):
            return rx.toast.error("Todos los campos y al menos una imagen son requeridos.")

        with rx.session() as session:
            new_product = Product(
                title=title,
                content=content,
                price=float(price),
                image_urls=self.temp_images,
                is_published=True,
            )
            session.add(new_product)
            session.commit()

        self.temp_images = []
        yield rx.toast.success("¡Producto creado con éxito!")
        return rx.set_val("form-create-product", "")

    # ... (El resto de los métodos no cambian) ...
    @rx.event
    def load_products(self):
        """Carga los productos publicados para la página principal."""
        with rx.session() as session:
            self.products = session.query(Product).where(Product.is_published == True).all()

    @rx.event
    def load_product_detail(self):
        """Carga el detalle de un producto para su página dinámica."""
        product_id = self.router.page.params.get("product_id", "0")
        with rx.session() as session:
            self.product_detail = session.get(Product, int(product_id))

    @rx.var
    def cart_items_count(self) -> int:
        """Calcula el número total de artículos en el carrito."""
        return sum(self.cart.values())

    @rx.event
    def add_to_cart(self, product_id: int):
        """Añade un producto al carrito y muestra una notificación."""
        if product_id not in self.cart:
            self.cart[product_id] = 0
        self.cart[product_id] += 1
        return rx.toast.info(f"Producto añadido al carrito. Total: {self.cart[product_id]}")