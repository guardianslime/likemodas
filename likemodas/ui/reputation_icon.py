# likemodas/ui/reputation_icon.py

import reflex as rx
from ..models import UserReputation

def reputation_icon(reputation: str, author_initial: str) -> rx.Component:
    """Displays the user's reputation icon."""
    crown_map = {
        UserReputation.WOOD.value: "🪵",
        UserReputation.COPPER.value: "🥉",
        UserReputation.SILVER.value: "🥈",
        UserReputation.GOLD.value: "🥇",
        UserReputation.DIAMOND.value: "💎",
    }
    return rx.avatar(
        fallback=crown_map.get(reputation, author_initial),
        size="2",
    )