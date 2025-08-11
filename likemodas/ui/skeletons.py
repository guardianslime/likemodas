# likemodas/ui/skeletons.py

import reflex as rx


def skeleton_navbar() -> rx.Component:
    """Un esqueleto estático para la barra de navegación pública."""
    return rx.box(
        rx.grid(
            rx.hstack(
                rx.box(width="8em", height="36px", bg=rx.color("gray", 4), border_radius="md"),
                align="center", spacing="4", justify="start",
            ),
            rx.box(height="36px", bg=rx.color("gray", 4), border_radius="md", width="100%"),
            rx.hstack(
                rx.box(width="36px", height="36px", bg=rx.color("gray", 4), border_radius="full"),
                rx.box(width="36px", height="36px", bg=rx.color("gray", 4), border_radius="full"),
                align="center", spacing="3", justify="end",
            ),
            columns="auto 1fr auto", align_items="center", width="100%", gap="1.5rem",
        ),
        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1.5rem", z_index="999",
        bg="#2C004BF0", 
        style={"backdrop_filter": "blur(10px)"},
    )

def skeleton_block(height: str, width: str = "100%", **props) -> rx.Component:
    """Un bloque de esqueleto genérico y reutilizable con animación de pulso."""
    return rx.box(
        height=height,
        width=width,
        bg=rx.color("gray", 4),
        border_radius="md",
        animation="pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        **props
    )

def skeleton_product_card() -> rx.Component:
    """Un esqueleto que imita las dimensiones y estructura de una tarjeta de producto."""
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

def skeleton_product_gallery(count: int = 8) -> rx.Component:
    """Muestra una cuadrícula de esqueletos de tarjetas de producto."""
    return rx.flex(
        rx.foreach(
            rx.Var.range(count),
            lambda _: skeleton_product_card()
        ),
        wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
    )

def skeleton_product_detail_view() -> rx.Component:
    """Un esqueleto para la página de detalle del producto."""
    image_section = skeleton_block(height="500px", width="100%")
    
    info_section = rx.vstack(
        skeleton_block(height="40px", width="70%"),
        skeleton_block(height="20px", width="40%", margin_top="1em"),
        skeleton_block(height="30px", width="30%", margin_top="1em"),
        skeleton_block(height="100px", width="100%", margin_top="2em"),
        skeleton_block(height="48px", width="100%", margin_top="2em"),
        align_items="start",
        spacing="4",
        width="100%"
    )

    return rx.grid(
        image_section,
        info_section,
        columns={"base": "1", "md": "2"},
        spacing="4",
        align_items="start",
        width="100%",
        max_width="1400px",
        padding="2em",
    )