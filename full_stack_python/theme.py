from reflex.vars import Var
import reflex as rx

config = rx.Config(
    app_name="full_stack_python",
    theme=rx.theme(
        appearance="dark",
        extend={
            "breakpoints": {
                "sm": "640px",
                "md": "768px",
                "lg": "1024px",
                "xl": "1280px",
            }
        }
    )
)