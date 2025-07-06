import reflex as rx

class State(rx.State):
    # Imágenes que el usuario ha subido (por publicación)
    publicaciones: list[list[str]] = []
    # Imágenes seleccionadas pero no subidas aún (previsualización local)
    previsualizacion: list[str] = []

  
    def actualizar_previsualizacion(self, archivos):
        # Actualiza la lista de previsualización con los nombres de los archivos seleccionados
        self.previsualizacion = archivos


    async def handle_upload(self, files: list[rx.UploadFile]):
        nombres = []
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            nombres.append(file.name)
        # Añade la publicación (grupo de imágenes) y limpia la previsualización
        self.publicaciones.append(nombres)
        self.previsualizacion = []

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
            # Quita el on_change aquí
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
        padding="2em"
    )

app = rx.App()
app.add_page(index, route="/")