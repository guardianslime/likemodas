# En: likemodas/utils/formatting.py

from typing import Optional
import reflex as rx

def format_to_cop(price: rx.Var[Optional[float]]) -> rx.Var[str]:
    """
    [CORREGIDO] Formatea un número o una Var a moneda COP de forma segura.
    Usa rx.cond para manejar valores nulos o cero en la interfaz.
    """
    return rx.cond(
        price > 0,
        # ✨ --- INICIO DE LA CORRECCIÓN CLAVE --- ✨
        # La forma correcta de pasar una Var a call_script es usando un f-string
        # para incrustar la variable directamente en el script.
        rx.call_script(
            f"new Intl.NumberFormat('es-CO', {{ style: 'currency', currency: 'COP', maximumFractionDigits: 0 }}).format({price.to(str)})"
        ),
        # ✨ --- FIN DE LA CORRECCIÓN CLAVE --- ✨
        "$ 0"
    )