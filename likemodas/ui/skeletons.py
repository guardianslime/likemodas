import reflex as rx

def skeleton_block(height: str, width: str = "100%", **props) -> rx.Component:
    """Un bloque de esqueleto genérico y reutilizable con animación."""
    return rx.box(
        height=height,
        width=width,
        bg=rx.color("gray", 4),
        border_radius="md",
        # La animación se puede definir globalmente en el tema si se desea
        animation="pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        # Permite pasar propiedades adicionales como márgenes
        **props
    )

def skeleton_product_card() -> rx.Component:
    """Un esqueleto que imita la tarjeta de un producto en la galería."""
    return rx.box(
        rx.vstack(
            skeleton_block(height="260px"),
            skeleton_block(height="24px", width="80%", margin_top="1em"),
            skeleton_block(height="24px", width="50%", margin_top="0.5em"),
            skeleton_block(height="21px", width="60%", margin_top="1em"),
            rx.spacer(),
            skeleton_block(height="40px", margin_top="1em"),
            spacing="2",
            height="100%"
        ),
        width="290px",
        height="450px",
        padding="1em",
        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px",
        box_shadow="md",
    )