import reflex as rx

def blog_post_not_found() -> rx.Component:
    return rx.hstack(
        rx.heading("Blog PostNot Found"), spacing="5",
        align="center",
        min_height="85vh")
