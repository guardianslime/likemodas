# likemodas/logic/shipping_calculator.py (LÓGICA ADAPTATIVA)

from collections import deque
# AHORA IMPORTAMOS EL DICCIONARIO MAESTRO
from ..data.geography_data import CITY_SPECIFIC_DATA

def find_shortest_commune_path(start_commune: int, end_commune: int, adjacency_graph: dict) -> list[int]:
    """
    Encuentra la ruta más corta entre dos comunas usando un grafo de adyacencia específico.
    """
    if start_commune not in adjacency_graph or end_commune not in adjacency_graph:
        return []

    queue = deque([[start_commune]])
    visited = {start_commune}

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == end_commune:
            return path

        for neighbor in adjacency_graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    
    return []

def calculate_dynamic_shipping(
    base_cost: float, 
    seller_barrio: str | None, 
    buyer_barrio: str | None,
    seller_city: str | None,
    buyer_city: str | None
) -> float:
    """
    Calcula el costo de envío final seleccionando dinámicamente los datos
    geográficos de la ciudad correspondiente.
    """
    if seller_city and buyer_city and seller_city != buyer_city:
        return 15000.0

    # --- INICIO DE LA MODIFICACIÓN CLAVE ---
    
    # 1. Obtener los datos específicos de la ciudad del envío (si existen)
    city_data = CITY_SPECIFIC_DATA.get(seller_city)

    # Si no tenemos un mapa de comunas para esta ciudad, o faltan datos, devolvemos el costo base.
    if not city_data or not seller_barrio or not buyer_barrio:
        return base_cost
    
    # 2. Extraer el mapa de barrios y el grafo de adyacencia de la ciudad correcta
    barrio_a_comuna_map = city_data["barrio_map"]
    comuna_adjacency_graph = city_data["adjacency"]

    # --- FIN DE LA MODIFICACIÓN CLAVE ---

    if seller_barrio == buyer_barrio:
        return base_cost

    seller_commune = barrio_a_comuna_map.get(seller_barrio)
    buyer_commune = barrio_a_comuna_map.get(buyer_barrio)

    if not seller_commune or not buyer_commune:
        return base_cost
        
    if seller_commune == buyer_commune:
        distance_cost = 2000.0
    else:
        # Pasamos el grafo de adyacencia correcto a la función de búsqueda
        path = find_shortest_commune_path(seller_commune, buyer_commune, comuna_adjacency_graph)
        if not path:
            distance_cost = 12000.0
        else:
            num_jumps = len(path) - 1
            distance_cost = num_jumps * 4000.0

    total_shipping_cost = min(base_cost + distance_cost, 12000.0)
    
    return total_shipping_cost