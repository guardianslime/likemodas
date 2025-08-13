# likemodas/pages/test_page.py

import reflex as rx
from ..ui.base import base_page

class TestState(rx.State):
    # Un estado mínimo con solo la variable para la ruta dinámica
    test_param: str = ""

def test_page() -> rx.Component:
    return base_page(
        rx.heading(f"El parámetro de prueba es: {TestState.test_param}")
    )
