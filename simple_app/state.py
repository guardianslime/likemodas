"""El estado de la aplicación."""

import reflex as rx

class State(rx.State):
    """El estado base de la aplicación.
    
    El estado es la fuente de verdad de la aplicación.
    """
    count: int = 0

    def increment(self):
        """Incrementa el contador."""
        self.count += 1

    def decrement(self):
        """Decrementa el contador."""
        self.count -= 1
