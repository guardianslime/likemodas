import reflex as rx

class GalleryState(rx.State):
    galerias: dict[str, list[str]] = {}
    galeria_actual: str = ""
    nueva_galeria: str = ""

    @rx.event
    def set_nueva_galeria(self, value: str):
        self.nueva_galeria = value

    @rx.event
    def crear_galeria(self):
        nombre = self.nueva_galeria.strip()
        if nombre and nombre not in self.galerias:
            self.galerias[nombre] = []
            self.galeria_actual = nombre
            self.nueva_galeria = ""

    @rx.event
    def seleccionar_galeria(self, nombre: str):
        self.galeria_actual = nombre

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not self.galeria_actual:
            return
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            self.galerias[self.galeria_actual].append(file.name)

def index():
    return rx.vstack(
        rx.hstack(
            rx.input(
                placeholder="Nombre de la nueva galería",
                value=GalleryState.nueva_galeria,
                on_change=GalleryState.set_nueva_galeria,
                width="200px",
            ),
            rx.button(
                "Crear galería",
                on_click=GalleryState.crear_galeria,
            ),
        ),
        rx.hstack(
            rx.text("Galería actual:"),
            rx.select(
                list(GalleryState.galerias.keys()),
                value=GalleryState.galeria_actual,
                on_change=GalleryState.seleccionar_galeria,
                placeholder="Selecciona una galería",
                width="200px",
            ),
        ),
        rx.cond(
            GalleryState.galeria_actual != "",
            rx.vstack(
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
                rx.button(
                    "Subir imágenes",
                    on_click=GalleryState.handle_upload(rx.upload_files(upload_id="image_upload")),
                ),
                rx.grid(
                    rx.foreach(
                        GalleryState.galerias[GalleryState.galeria_actual],
                        lambda filename: rx.image(
                            src=rx.get_upload_url(filename),
                            width="200px",
                            height="auto",
                            style={"objectFit": "cover", "margin": "0.5em"},
                        ),
                    ),
                    columns="3",
                    spacing="2",
                ),
            ),
            rx.text("Crea y selecciona una galería para subir imágenes."),
        ),
        rx.divider(),
        rx.text("Todas las galerías:"),
        rx.foreach(
            GalleryState.galerias.items(),
            lambda item: rx.vstack(
                rx.text(f"Galería: {item[0]}"),
                rx.grid(
                    rx.foreach(
                        item[1],
                        lambda filename: rx.image(
                            src=rx.get_upload_url(filename),
                            width="100px",
                            height="auto",
                            style={"objectFit": "cover", "margin": "0.25em"},
                        ),
                    ),
                    columns="5",
                    spacing="1",
                ),
                style={"marginBottom": "2em"},
            ),
        ),
        padding="2em"
    )

app = rx.App()
app.add_page(index, route="/")