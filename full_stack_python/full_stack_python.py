import reflex as rx

class State(rx.State):
    publicaciones: list[list[str]] = []
    img_idx: int = 0  # Índice de la imagen actual en galería

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        nombres = []
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            nombres.append(file.name)
        self.publicaciones.append(nombres)

    @rx.var
    def imagenes(self) -> list[str]:
        # Junta todas las imágenes de todas las publicaciones
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
        ),
        rx.text("Previsualización:"),
        rx.hstack(
            rx.foreach(
                rx.selected_files("image_upload"),
                lambda f: rx.image(src=f, width="150px"),
            ),
        ),
        rx.button(
            "Subir imágenes",
            on_click=State.handle_upload(rx.upload_files(upload_id="image_upload")),
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