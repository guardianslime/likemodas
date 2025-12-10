import reflex as rx

def delete_account_info() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("triangle_alert", size=48, color="red"), # Asegúrate de tener lucide icons o usa texto
            rx.heading("Eliminación de Cuenta y Datos", size="7"),
            
            rx.text(
                "En LikeModas nos tomamos tu privacidad en serio. "
                "Si deseas eliminar permanentemente tu cuenta y todos tus datos asociados, "
                "tienes las siguientes opciones:",
                text_align="center",
                color="gray"
            ),
            
            rx.divider(),
            
            rx.heading("Opción 1: Desde la App o Web (Automático)", size="4"),
            rx.text(
                "1. Inicia sesión en tu cuenta.\n"
                "2. Ve a tu Perfil > Seguridad.\n"
                "3. En la 'Zona de Peligro', selecciona 'Eliminar Cuenta'.",
                white_space="pre-line" # Para respetar los saltos de línea
            ),
            
            rx.button(
                "Ir a Iniciar Sesión",
                on_click=rx.redirect("/login"), # Ajusta a tu ruta de login
                variant="solid",
                color_scheme="blue"
            ),
            
            rx.divider(),
            
            rx.heading("Opción 2: Solicitud Manual", size="4"),
            rx.text(
                "Si no tienes acceso a tu cuenta, puedes solicitar la eliminación manual "
                "enviando un correo desde la dirección registrada:",
                text_align="center"
            ),
            rx.code("soporte@likemodas.com"),
            rx.text(
                "Asunto: SOLICITUD DE BORRADO DE DATOS",
                font_weight="bold"
            ),
            
            spacing="6",
            padding="2em",
            max_width="600px",
            border="1px solid #eaeaea",
            border_radius="12px",
            box_shadow="lg",
            background="white"
        ),
        width="100%",
        min_height="100vh",
        background_color="#f5f5f5",
        padding="20px"
    )