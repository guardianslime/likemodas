import reflex as rx
import os

class State(rx.State):
    publicaciones: list[list[str]] = []
    imagenes_temporales: list[str] = []
    img_idx: int = 0  # Índice de la imagen actual en galería

    @rx.event
    async def on_startup(self):
        # Cargar imágenes persistentes al iniciar la app
        upload_dir = rx.get_upload_dir()
        if upload_dir.exists():
            archivos = [f.name for f in upload_dir.iterdir() if f.is_file()]
            if archivos and not self.publicaciones:
                self.publicaciones.append(archivos)

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            if file.name not in self.imagenes_temporales:
                self.imagenes_temporales.append(file.name)

    @rx.event
    def eliminar_imagen_temp(self, nombre):
        if nombre in self.imagenes_temporales:
            self.imagenes_temporales.remove(nombre)

    @rx.event
    def publicar(self):
        if self.imagenes_temporales:
            self.publicaciones.append(self.imagenes_temporales.copy())
            self.imagenes_temporales = []

    @rx.var
    def imagenes(self) -> list[str]:
        # Junta todas las imágenes publicadas de todas las publicaciones
        return [img for grupo in self.publicaciones for img in grupo]
    
    @rx.var
    def num_imagenes(self) -> int:
        return len(self.imagenes)

    @rx.event
    def siguiente(self):
        if self.img_idx < self.num_imagenes - 1:
            self.img_idx += 1

    @rx.event
    def anterior(self):
        if self.img_idx > 0:
            self.img_idx -= 1

def index():
    return rx.vstack(
        rx.upload(
            rx.text("Arrastra imágenes aquí o haz clic para seleccionarlas"),
            id="image_upload",
            accept={
                "image/png": [".png"],
                "image/jpeg": [".jpg", ".jpeg"],
                "image/gif": [".gif"],
                "image/webp": [".webp"],
            },
            max_files=10,
            multiple=True,
            border="2px dashed #60a5fa",
            padding="2em",
            on_drop=State.handle_upload(rx.upload_files(upload_id="image_upload")),
        ),
        rx.text("Previsualización:"),
        rx.cond(
            State.imagenes_temporales,
            rx.hstack(
                rx.foreach(
                    State.imagenes_temporales,
                    lambda f: rx.box(
                        rx.image(src=rx.get_upload_url(f), width="150px"),
                        rx.icon(
                            tag="trash",
                            style={
                                "position": "absolute",
                                "top": "8px",
                                "right": "8px",
                                "cursor": "pointer",
                                "color": "red",
                                "background": "white",
                                "borderRadius": "50%",
                                "padding": "2px",
                                "boxShadow": "0 1px 2px rgba(0,0,0,0.15)",
                            },
                            on_click=State.eliminar_imagen_temp(f),
                        ),
                        style={
                            "position": "relative",
                            "display": "inline-block",
                            "margin": "8px",
                        },
                    ),
                ),
            ),
            rx.text("No hay imágenes para previsualizar."),
        ),
        rx.button(
            "Publicar",
            on_click=State.publicar,
            disabled=~State.imagenes_temporales,
            color_scheme="green"
        ),
        rx.link("Ver galería", href="/galeria"),
        padding="2em"
    )

def galeria():
    return rx.center(
        rx.cond(
            State.num_imagenes > 0,
            rx.vstack(
                rx.image(
                    src=rx.get_upload_url(State.imagenes[State.img_idx]),
                    width="400px",
                ),
                rx.hstack(
                    rx.button("Anterior", on_click=State.anterior, disabled=State.img_idx == 0),
                    rx.button(
                        "Siguiente",
                        on_click=State.siguiente,
                        disabled=State.img_idx == State.num_imagenes - 1,
                    ),
                ),
                rx.text(f"{State.img_idx + 1} / {State.num_imagenes}"),
            ),
            rx.text("No hay imágenes publicadas."),
        ),
        padding="2em"
    )

app = rx.App()
app.add_page(index, route="/")
app.add_page(galeria, route="/galeria")
app.add_event_handler("startup", State.on_startup)