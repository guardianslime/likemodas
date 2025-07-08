import reflex as rx
from typing import List, Dict, Any
import time

class BlogState(rx.State):
    """
    Un estado simple que maneja el blog en memoria, similar al código de referencia.
    """
    
    # Guarda los posts como una lista de diccionarios.
    # Cada diccionario contendrá: title, content, images, y un id único.
    posts: List[Dict[str, Any]] = []

    # --- Lógica para el formulario de añadir post ---
    imagenes_temporales: List[str] = []
    form_data: Dict[str, str] = {}
    
    def set_form_field(self, field: str, value: str):
        """Actualiza los campos de texto del formulario (título y contenido)."""
        self.form_data[field] = value

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la carga de imágenes al directorio de uploads del servidor."""
        for file in files:
            upload_data = await file.read()
            # Usamos filename para consistencia entre navegadores
            path = rx.get_upload_dir() / file.filename
            with path.open("wb") as f:
                f.write(upload_data)
            
            if file.filename not in self.imagenes_temporales:
                self.imagenes_temporales.append(file.filename)

    def eliminar_imagen_temp(self, img_name: str):
        """Elimina una imagen de la lista de previsualización."""
        self.imagenes_temporales.remove(img_name)

    def publicar_post(self):
        """
        Crea el post en memoria, lo añade a la lista 'posts' y limpia el formulario.
        """
        if not self.form_data.get("title") or not self.form_data.get("content"):
            return rx.window_alert("Por favor, rellena el título y el contenido.")
            
        nuevo_post = {
            "title": self.form_data.get("title", "Sin Título"),
            "content": self.form_data.get("content", ""),
            "images": self.imagenes_temporales.copy(),
            # Usamos el timestamp como un ID simple y único para poder borrarlo
            "id": int(time.time() * 1000)
        }
        self.posts.append(nuevo_post)
        
        # Limpiar el estado para el siguiente post
        self.imagenes_temporales = []
        self.form_data = {}
        
        # Redirige al usuario a la página principal del blog
        return rx.redirect("/blog")

    def eliminar_post(self, post_id: int):
        """Encuentra y elimina un post de la lista en memoria usando su ID."""
        self.posts = [p for p in self.posts if p.get("id") != post_id]