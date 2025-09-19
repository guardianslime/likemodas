# likemodas/services/qr_service.py
import qrcode
import io
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask

def generate_qr_code_in_memory(data: str) -> io.BytesIO:
    """
    Genera una imagen de código QR para los datos proporcionados y la devuelve
    como un objeto BytesIO en memoria.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Crea la imagen QR con un estilo visual que coincide con el tema de la app
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(
            front_color=(79, 70, 229) # Tono violeta similar al de la UI
        )
    )

    # Guarda la imagen en un búfer de memoria en lugar de un archivo
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0) # Rebobina el búfer al principio para su lectura posterior
    return buffer