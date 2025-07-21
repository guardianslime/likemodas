import reflex as rx
from .. import navigation

def my_account_redirect_page() -> rx.Component:
    """
    Página de redirección para la ruta principal de "Mi Cuenta".
    Redirige a la primera sub-página por defecto, como la información de envío.
    """
    # Redirige a la página de información de envío que ya tienes creada.
    return rx.redirect(navigation.routes.SHIPPING_INFO_ROUTE)