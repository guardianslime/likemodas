# likemodas/ui/vote_buttons.py

import reflex as rx
from ..state import AppState

def vote_buttons(comment_id: int, likes: int, dislikes: int, user_vote: str) -> rx.Component:
    """Displays like and dislike buttons for a comment."""
    return rx.hstack(
        rx.button(
            rx.icon("thumbs-up"),
            f"{likes}",
            on_click=lambda: AppState.vote_on_comment(comment_id, "like"),
            # --- CORRECCIÓN AQUÍ: Se usa rx.cond en lugar de if/else ---
            color_scheme=rx.cond(user_vote == "like", "green", "gray"),
            variant=rx.cond(user_vote == "like", "soft", "outline"),
        ),
        rx.button(
            rx.icon("thumbs-down"),
            f"{dislikes}",
            on_click=lambda: AppState.vote_on_comment(comment_id, "dislike"),
            # --- CORRECCIÓN AQUÍ: Se usa rx.cond en lugar de if/else ---
            color_scheme=rx.cond(user_vote == "dislike", "red", "gray"),
            variant=rx.cond(user_vote == "dislike", "soft", "outline"),
        ),
        spacing="3",
    )