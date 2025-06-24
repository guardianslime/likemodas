import reflex as rx 

# --- CORRECCIÓN ---
# Se cambia la importación para que apunte a la carpeta 'blog' en lugar de 'articles'.
from ..blog.list import blog_public_list_component
from .. import navigation

def landing_component() -> rx.Component:
    """
    La página de bienvenida que ven los usuarios no autenticados.
    Muestra una lista de los posts públicos más recientes.
    """
    return rx.vstack(
        rx.heading("Bienvenido a SaaS", size="9"),
        rx.link(
            rx.button("Sobre Nosotros", color_scheme='gray'),
            href=navigation.routes.ABOUT_US_ROUTE
        ),
        rx.divider(),
        rx.heading("Publicaciones Recientes", size="5"),
        
        # Usamos el componente correcto que ahora vive en el módulo 'blog'.
        blog_public_list_component(columns=1, limit=3),
        
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    )
