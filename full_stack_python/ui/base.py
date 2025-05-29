import reflex as rx

from .nav import navbar
from .dashboard import base_dashboard_page

def base_layout_component(child, *args, **Kwargs) -> rx.Component:

    return rx.fragment(
        navbar(),
        rx.box(
            child,
            #bg=rx.color("accent", 3),
            padding="1em",
            width="100%",    
            id="my-content-area-el"
        ),
        rx.logo(),
        rx.color_mode.button(position= "bottom-left"),
        id="my-base-container",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    is_logged_in = True
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not valid child element")
    return rx.cond(
        is_logged_in,
        base_dashboard_page(child, *args, **kwargs),
        base_layout_component(child, *args, **kwargs),
    )

