# En: likemodas/utils/formatting.py

from typing import Optional
import reflex as rx # ✨ 1. AÑADE ESTA IMPORTACIÓN ✨

def format_to_cop(price: rx.Var[Optional[float]]) -> rx.Var[str]:
    """
    [CORREGIDO] Formatea un número o una Var a moneda COP de forma segura.
    Usa rx.cond para manejar valores nulos o cero en la interfaz.
    """
    # ✨ 2. REEMPLAZA LA LÓGICA ANTERIOR CON ESTA ✨
    return rx.cond(
        price > 0,
        "$" + rx.call_script(
            f"{{_val: {price.to(str)}}}.toLocaleString('es-CO', {{ style: 'decimal', maximumFractionDigits: 0 }})",
            _val=0,
        ),
        "$ 0"
    )