# full_stack_python/contact/page.py

# ... (las importaciones no cambian) ...

def contact_entry_list_item(contact: ContactEntryModel) -> rx.Component:
    """Muestra una entrada de contacto individual en la lista."""
    return rx.box(
        rx.heading(f"{contact.first_name} ({contact.email})", size="4"),
        rx.text(contact.message, white_space="pre-wrap", margin_y="0.5em"),
        
        # ¡CORRECCIÓN! Ahora usamos el campo calculado 'created_at_formatted'.
        rx.text(f"Recibido el: {contact.created_at_formatted}", size="2", color_scheme="gray"),
        
        rx.cond(
            contact.userinfo_id,
            rx.text("Enviado por un usuario registrado", size="2", weight="bold"),
            rx.text("Enviado por un invitado", size="2", weight="bold"),
        ),
        padding="1em", border="1px solid", border_color=rx.color("gray", 6), border_radius="0.5em", width="100%"
    )

# ... (el resto del archivo no cambia) ...