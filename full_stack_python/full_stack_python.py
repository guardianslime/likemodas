import reflex as rx

class State(rx.State):
    publicaciones: list[list[str]] = []

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
        rx.text("Publicaciones:"),
        rx.foreach(
            State.publicaciones,
            lambda grupo: rx.hstack(
                rx.foreach(
                    grupo,
                    lambda filename: rx.image(src=rx.get_upload_url(filename), width="150px"),
                ),
                margin_bottom="1em"
            ),
        ),
        padding="2em"
    )

app = rx.App()