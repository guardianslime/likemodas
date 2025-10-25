# En: likemodas/utils/formatting.py

from typing import Optional, Union
import reflex as rx

def format_to_cop(price: Union[rx.Var[Optional[float]], Optional[float]]) -> Union[rx.Var[str], str]:
    """
    Función de formato PÚBLICA. Solo para el frontend (componentes de UI).
    """
    if isinstance(price, (int, float)):
        # Maneja números estáticos (por si acaso)
        if price is None or price < 1:
            return "$ 0"
        formatted_number = f"{price:,.0f}"
        colombian_format = formatted_number.replace(',', '.')
        return f"$ {colombian_format}"

    # Maneja TODAS las variables de Reflex (rx.Var, NumberCastedVar, etc.)
    return rx.cond(
        price > 0,
        rx.call_script(
            f"new Intl.NumberFormat('es-CO', {{ style: 'currency', currency: 'COP', maximumFractionDigits: 0 }}).format({price.to(str)})"
        ),
        "$ 0"
    )