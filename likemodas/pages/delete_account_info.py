# likemodas/pages/delete_account_info.py

import reflex as rx

def delete_account_info() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Icono de alerta en rojo brillante para resaltar sobre negro
            rx.icon("triangle_alert", size=48, color="#ff4444"), 
            
            rx.heading("Eliminación de Cuenta y Datos", size="7", color="white"),
            
            rx.text(
                "En LikeModas nos tomamos tu privacidad en serio. "
                "Si deseas eliminar permanentemente tu cuenta y todos tus datos asociados, "
                "tienes las siguientes opciones:",
                text_align="center",
                color="#cccccc" # Gris claro para lectura cómoda
            ),
            
            rx.divider(border_color="#333333"), # Divisor sutil
            
            # --- Opción 1 ---
            rx.heading("Opción 1: Desde la App o Web (Automático)", size="4", color="white"),
            rx.text(
                "1. Inicia sesión en tu cuenta.\n"
                "2. Ve a tu Perfil > Configuración.\n"
                "3. Baja hasta el final y selecciona 'Eliminar Cuenta'.",
                white_space="pre-line",
                color="#eeeeee"
            ),
            
            rx.button(
                "Ir a Iniciar Sesión",
                on_click=rx.redirect("/login"),
                variant="solid",
                color_scheme="blue", # Botón azul resalta bien en negro
                cursor="pointer"
            ),
            
            rx.divider(border_color="#333333"),
            
            # --- Opción 2 ---
            rx.heading("Opción 2: Solicitud Manual", size="4", color="white"),
            rx.text(
                "Si no tienes acceso a tu cuenta, puedes solicitar la eliminación manual "
                "enviando un correo desde la dirección registrada:",
                text_align="center",
                color="#cccccc"
            ),
            rx.code("soporte@likemodas.com", color_scheme="green", variant="soft"),
            rx.text(
                "Asunto: SOLICITUD DE BORRADO DE DATOS",
                font_weight="bold",
                color="white"
            ),
            
            spacing="6",
            padding="2em",
            max_width="600px",
            width="100%",
            # Estilos de la tarjeta oscura
            border="1px solid #333333",
            border_radius="12px",
            box_shadow="0 4px 20px rgba(0, 0, 0, 0.5)",
            background="#1a1a1a" # Gris muy oscuro (Casi negro) para la tarjeta
        ),
        # Estilos del fondo de toda la página
        width="100%",
        min_height="100vh",
        background="black", # Fondo negro puro
        padding="1em"
    )