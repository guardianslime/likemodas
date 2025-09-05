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
            color_scheme="green" if user_vote == "like" else "gray",
            variant="soft" if user_vote == "like" else "outline",
        ),
        rx.button(
            rx.icon("thumbs-down"),
            f"{dislikes}",
            on_click=lambda: AppState.vote_on_comment(comment_id, "dislike"),
            color_scheme="red" if user_vote == "dislike" else "gray",
            variant="soft" if user_vote == "dislike" else "outline",
        ),
        spacing="3",
    )