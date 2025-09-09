# likemodas/pages/payment_status.py
import reflex as rx

def payment_status_page() -> rx.Component:
    """Página que informa al usuario mientras se procesa el pago de forma asíncrona."""
    return rx.center(
        rx.vstack(
            rx.heading("Procesando tu pago..."),
            rx.text("Estamos esperando la confirmación de Wompi."),
            rx.text("Recibirás una notificación y tu orden se actualizará automáticamente una vez que se complete el proceso."),
            rx.spinner(size="3"),
            rx.link(
                rx.button("Ver el estado de mis compras", variant="soft"),
                href="/my-purchases",
                margin_top="2em"
            ),
            spacing="5",
            align="center"
        ),
        min_height="85vh"
    )