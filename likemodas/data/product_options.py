# likemodas/data/product_options.py

# Listas de Tipos (existentes)
LISTA_TIPOS_ROPA = [
    "Abrigo", "Blusa", "Body", "Buzo", "Camisa", "Camiseta", "Cárdigan", "Chaleco", 
    "Chaqueta", "Conjunto", "Corsé", "Falda", "Gabardina", "Jeans", "Jogger", 
    "Leggings", "Overol", "Pantalón", "Polo", "Short", "Sudadera", "Suéter", 
    "Top", "Vestido", "Otro"
]

LISTA_TIPOS_ZAPATOS = [
    "Baletas", "Botas", "Botines", "Chanclas", "Mocasines", "Pantuflas", 
    "Sandalias", "Tenis", "Zapatillas", "Zapatos de Tacón", "Zuecos", "Otro"
]

LISTA_TIPOS_MOCHILAS = [
    "Antirrobo", "Bandolera", "Bolsa de Lona", "Deportiva", "Escolar", "Maletín",
    "Mochila de Acampada", "Mochila de Viaje", "Mochila Urbana", "Morral", "Otro"
]

LISTA_TIPOS_GENERAL = sorted(list(set(
    LISTA_TIPOS_ROPA + LISTA_TIPOS_ZAPATOS + LISTA_TIPOS_MOCHILAS
)))

# --- LISTAS DE CARACTERÍSTICAS ACTUALIZADAS Y AMPLIADAS ---

LISTA_COLORES = sorted([
    "Amarillo", "Azul", "Beige", "Blanco", "Café", "Dorado", "Gris", "Morado",
    "Naranja", "Negro", "Plateado", "Rojo", "Rosa", "Verde", "Vino", "Multicolor"
])

LISTA_TALLAS_ROPA = ["XS", "S", "M", "L", "XL", "XXL", "Talla Única"]

LISTA_NUMEROS_CALZADO = [str(i) for i in range(34, 45)]

# --- ✅ LISTA DE MATERIALES AMPLIADA ---
LISTA_MATERIALES = sorted([
    "Algodón", "Cuero", "Cuero Sintético", "Denim", "Lana", "Lino", "Lona", 
    "Licra", "Malla", "Nylon", "Pana", "Poliéster", "Seda", "Sintético", "Viscosa"
])

# --- ✅ NUEVA LISTA PARA TAMAÑO DE MOCHILAS ---
LISTA_TAMANOS_MOCHILAS = ["Pequeña", "Mediana", "Grande", "Extra Grande"]

# --- ✅ LISTA GENERAL DE MEDIDAS ACTUALIZADA ---
# Se añaden los tamaños de mochilas para que aparezcan en los filtros generales
LISTA_MEDIDAS_GENERAL = sorted(list(set(LISTA_TALLAS_ROPA + LISTA_NUMEROS_CALZADO + LISTA_TAMANOS_MOCHILAS)))