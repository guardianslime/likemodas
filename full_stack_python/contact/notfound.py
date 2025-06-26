import reflex as rx

def contact_entry_not_found() -> rx.Component:
    return rx.hstack(
        rx.heading("Contact EntryNot Found"), spacing="5",
        align="center",
        min_height="85vh")