# full_stack_python/blog/forms.py

import reflex as rx 

from .state import (
    BlogAddPostFormState,
    BlogEditFormState
)

# --- SIN CAMBIOS ---
# Este componente ya era correcto y no necesita modificaciones.
def blog_post_add_form() -> rx.Component:
    return rx.form(
            rx.vstack(
                rx.hstack(
                    rx.input(
                        name="title",
                        placeholder="Title",
                        required=False, # Considera cambiar a True si el título es obligatorio
                        type= "text",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.text_area(
                    name="content",
                    placeholder="Your message",
                    required=True,
                    height='50vh',
                    width='100%',
                ),
                rx.button("Submit", type="submit"),
            ),
            on_submit=BlogAddPostFormState.handle_submit,
            reset_on_submit=True,
    )

# --- CÓDIGO CORREGIDO ---
# Esta es la versión modificada que soluciona el error.
def blog_post_edit_form() -> rx.Component:
    """
    Un formulario para editar un post existente.
    Ahora está envuelto en un rx.cond para asegurar que el post se haya cargado
    antes de intentar renderizar los datos, evitando errores de 'None'.
    """
    return rx.cond(
        BlogEditFormState.post,  # Condición: renderizar solo si el post NO es None
        
        # Si el post existe, muestra el formulario
        rx.form(
            rx.box(
                rx.input(
                    type='hidden',
                    name='post_id',
                    # Ahora es seguro acceder a .id porque estamos dentro de la condición
                    value=BlogEditFormState.post.id
                ),
                display='none'
            ),
            rx.vstack(
                rx.hstack(
                    rx.input(
                        # Es mejor usar default_value para el valor inicial de un formulario
                        default_value=BlogEditFormState.post.title,
                        name="title",
                        placeholder="Title",
                        required=True,
                        type='text',
                        width='100%',
                    ),
                    width='100%',
                ),
                rx.text_area(
                    # 'value' es correcto aquí porque su cambio está controlado por on_change
                    value=BlogEditFormState.post_content,
                    on_change=BlogEditFormState.set_post_content,
                    name='content',
                    placeholder='Your message',
                    required=True,
                    height='50vh',
                    width='100%',
                ),
                rx.flex(
                    rx.switch(
                        # 'is_checked' es más explícito para un switch controlado por el estado
                        is_checked=BlogEditFormState.post_publish_active,
                        on_change=BlogEditFormState.set_post_publish_active,
                        name='publish_active',
                    ),
                    rx.text("Publish Active"),
                    spacing="2",
                ),
                rx.cond(
                    BlogEditFormState.post_publish_active,
                    rx.box(
                        rx.hstack(
                            rx.input(
                                default_value=BlogEditFormState.publish_display_date,
                                type='date',
                                name='publish_date',
                                width='100%'
                            ),
                            rx.input(
                                default_value=BlogEditFormState.publish_display_time,
                                type='time',
                                name='publish_time',
                                width='100%'
                            ),
                            width='100%'
                        ),
                        width='100%'
                    )
                ),
                rx.button("Submit", type="submit"),
                spacing="4", # Añadido espaciado para mejor apariencia
            ),
            on_submit=BlogEditFormState.handle_submit,
        ),

        # Si el post aún no se ha cargado (es None), muestra un spinner.
        # Esto soluciona el error y mejora la experiencia de usuario.
        rx.center(rx.spinner(size="3"), height="50vh")
    )