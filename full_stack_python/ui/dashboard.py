# full_stack_python/pages/dashboard.py
import reflex as rx
from ..articles.list import componente_de_prueba

def dashboard_component() -> rx.Component:
    """Un dashboard que solo importa el componente de prueba."""
    return rx.vstack(
        rx.heading("Página de Prueba"),
        componente_de_prueba(),
    )