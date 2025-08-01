# likemodas/utils/formatting.py
import locale

def format_to_cop(price: float) -> str:
    """Formatea un número al estilo de pesos colombianos."""
    if price is None:
        return "$ 0"
    try:
        # Intenta usar la configuración regional de Colombia
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        # Formatea la moneda, quitando los decimales
        return locale.currency(price, grouping=True, symbol=True).split(',')[0]
    except (locale.Error, ValueError):
        # Si falla, usa un método manual que reemplaza comas por puntos
        price_int = int(price)
        return f"$ {price_int:,}".replace(",", ".")
