import reflex as rx

class State(rx.State):
    pass

def index():
    return rx.text("¡Hola, Reflex desplegado en Railway y Vercel!")

app = rx.App()
app.add_page(index)