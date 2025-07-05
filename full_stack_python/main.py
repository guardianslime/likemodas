import reflex as rx

class State(rx.State):
    """Estado de la app."""
    uploaded_files: list[str] = []

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de archivos."""
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            self.uploaded_files.append(file.name)

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
        rx.button(
            "Subir imágenes",
            on_click=State.handle_upload(rx.upload_files(upload_id="image_upload")),
        ),
        rx.grid(
            rx.foreach(
                State.uploaded_files,
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
        padding="2em"
    )

app = rx.App()
app.add_page(index, route="/")