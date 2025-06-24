import reflex as rx 

# --- CORRECCIÓN ---
# Se importa el componente para listar posts desde el módulo 'blog', no 'articles'.
from ..blog.list import blog_public_list_component

def dashboard_component() -> rx.Component:
    """
    El panel principal que ve el usuario al iniciar sesión.
    """
    return rx.box(
        rx.heading("Bienvenido de nuevo", size='2'),
        rx.divider(margin_y='1em'), # margin_y es un atajo para margin_top y margin_bottom
        
        # --- CORRECCIÓN ---
        # Usamos el nuevo componente que carga los posts públicos desde el módulo 'blog'.
        blog_public_list_component(columns=3, limit=20),
        
        min_height="85vh",
    )
