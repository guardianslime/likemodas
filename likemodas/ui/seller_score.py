# likemodas/ui/seller_score.py

import reflex as rx

def seller_score_stars(score: int) -> rx.Component:
    """Displays the seller's score as purple stars."""
    return rx.hstack(
        rx.foreach(
            rx.Var.range(5),
            lambda i: rx.icon(
                "star",
                color=rx.cond(score > i, "purple", rx.color("gray", 8)),
                style={"fill": rx.cond(score > i, "purple", "none")},
                size=20,
            )
        ),
        spacing="1",
    )