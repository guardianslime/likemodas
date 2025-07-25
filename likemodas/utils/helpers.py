# likemodas/utils/helpers.py

def get_unique_options_from_attributes(posts: list, attribute_keys: list[str]) -> list[dict]:
    """
    Extrae valores únicos de los atributos de los productos y los formatea
    para el componente de selección con búsqueda.
    """
    unique_values = set()
    for post in posts:
        for key in attribute_keys:
            value = post.attributes.get(key)
            if value and str(value).strip():
                unique_values.add(str(value).strip())
    
    return sorted([{"label": v, "value": v} for v in unique_values], key=lambda x: x["label"])