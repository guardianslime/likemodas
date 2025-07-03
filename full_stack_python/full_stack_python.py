import reflex as rx

# Tu código aquí, por ejemplo:
def index():
    return rx.text("¡Funciona!")

app = rx.App()
app.add_page(index, route="/")