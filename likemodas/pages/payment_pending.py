# likemodas/pages/payment_pending.py
import reflex as rx

def payment_pending_page() -> rx.Component:
    """Página que se muestra después de finalizar una compra online."""
    return rx.center(
        rx.vstack(
            rx.icon(tag="check_check", size=64, color_scheme="green"),
            rx.heading("¡Tu pedido ha sido recibido!", size="7"),
            rx.text(
                "Gracias por tu compra. El vendedor ha sido notificado y te enviará el enlace de pago en breve.",
                text_align="center",
                max_width="500px",
                margin_top="1em"
            ),
            rx.link(
                rx.button("Ver el estado de mis compras", margin_top="2em"),
                href="/my-purchases",
            ),
            spacing="5",
            align="center"
        ),
        min_height="85vh",
        padding="2em"
    )