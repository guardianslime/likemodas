import reflex as rx 

# --- CORRECCIÓN ---
# Apuntamos a la carpeta 'blog' para obtener el componente que lista los posts públicos.
from ..blog.list import blog_public_list_component

def dashboard_component() -> rx.Component:
    """
    El panel principal que ve el usuario al iniciar sesión.
    """
    return rx.box(
        rx.heading("Bienvenido de nuevo", size='2'),
        # Usar margin_y es un atajo para margin_top y margin_bottom.
        rx.divider(margin_y='1em'), 
        
        # Usamos el componente correcto que ahora vive en el módulo del blog.
        blog_public_list_component(columns=3, limit=20),
        
        min_height="85vh",
    )
