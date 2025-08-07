# likemodas/state.py

import reflex as rx
from sqlmodel import Field, Column, JSON
from typing import List, Dict, Optional
import asyncio

# --- MODELO DE DATOS ---
# Un solo modelo para simplificar.
class Product(rx.Model, table=True):
    title: str
    content: str
    price: float = 0.0
    image_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_published: bool = Field(default=False)


# --- ESTADO PRINCIPAL DE LA APP ---
class AppState(rx.State):
    """Estado único y simple de la aplicación."""

    # --- Productos ---
    # Lista de productos para la galería principal
    products: list[Product] = []
    # El producto que se está viendo en la página de detalle
    product_detail: Optional[Product] = None

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

    # --- Carrito de Compras ---
    cart: Dict[int, int] = {}

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

    # --- Panel de Administración ---
    temp_images: list[str] = []
    is_uploading: bool = False

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de imágenes y las guarda temporalmente."""
        self.is_uploading = True
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.filename
            outfile.write_bytes(upload_data)
            self.temp_images.append(file.filename)
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
                is_published=True, # Publicar inmediatamente
            )
            session.add(new_product)
            session.commit()

        # Limpiar formulario
        self.temp_images = []
        yield rx.toast.success("¡Producto creado con éxito!")
        # Usamos un evento para resetear el formulario del lado del cliente
        return rx.set_val("form-create-product", "")