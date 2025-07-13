import reflex as rx

class SearchState(rx.State):
    search_term: str = ""

    def update_search(self, value: str):
        self.search_term = value
        print(f"🔍 Buscando: {self.search_term}")

    def search_action(self):
        # Aquí puedes navegar a otra página o hacer un filtro
        print(f"🔎 Acción de búsqueda: {self.search_term}")
