import reflex as rx

from .nav import navbar

def base_page(child: rx.Component, hide_navbar=False, *args, **kwargs) -> rx.Component:
    # print(type(x) for x in args)
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not valid child element")
    if hide_navbar:
        return rx.container(
            child,
            rx.logo(),
            rx.color_mode.button(oosittion= "bottom-left"),
    )
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

