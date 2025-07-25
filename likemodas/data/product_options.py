# likemodas/data/product_options.py

def _format_for_select(options: list[str]) -> list[dict]:
    """Convierte una lista de strings al formato {"label": "...", "value": "..."}."""
    return [{"label": opt, "value": opt} for opt in options]

_ropa = [
    "Abrigo", "Blusa", "Body", "Buzo", "Camisa", "Camiseta", "Cárdigan", "Chaleco", 
    "Chaqueta", "Conjunto", "Corsé", "Falda", "Gabardina", "Jeans", "Jogger", 
    "Leggings", "Overol", "Pantalón", "Polo", "Short", "Sudadera", "Suéter", 
    "Top", "Vestido", "Otro"
]
LISTA_TIPOS_ROPA = _format_for_select(_ropa)

_zapatos = [
    "Baletas", "Botas", "Botines", "Chanclas", "Mocasines", "Pantuflas", 
    "Sandalias", "Tenis", "Zapatillas", "Zapatos de Tacón", "Zuecos", "Otro"
]
LISTA_TIPOS_ZAPATOS = _format_for_select(_zapatos)

_mochilas = [
    "Antirrobo", "Bandolera", "Bolsa de Lona", "Deportiva", "Escolar", "Maletín",
    "Mochila de Acampada", "Mochila de Viaje", "Mochila Urbana", "Morral", "Otro"
]
LISTA_TIPOS_MOCHILAS = _format_for_select(_mochilas)

# Se combinan todos los tipos, se eliminan duplicados y se ordena alfabéticamente.
LISTA_TIPOS_GENERAL = sorted(
    _format_for_select(list(set(_ropa + _zapatos + _mochilas))),
    key=lambda x: x["label"]
)