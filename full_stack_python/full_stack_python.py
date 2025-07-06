import reflex as rx
import os

class State(rx.State):
    uploaded_files: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar la lista con los archivos ya guardados en el volumen
        upload_dir = rx.get_upload_dir()
        if upload_dir.exists():
            self.uploaded_files = [
                f.name for f in upload_dir.iterdir() if f.is_file()
            ]

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            if file.name not in self.uploaded_files:
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
            "Subir imagen",
            on_click=State.handle_upload(rx.upload_files(upload_id="image_upload")),
        ),
        rx.foreach(
            State.uploaded_files,
            lambda filename: rx.image(src=rx.get_upload_url(filename), width="300px"),
        ),
        padding="2em"
    )

app = rx.App()
app.add_page(index, route="/")