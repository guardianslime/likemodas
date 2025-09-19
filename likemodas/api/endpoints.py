# likemodas/api/endpoints.py
from fastapi import APIRouter, Response
from ..services import qr_service

router = APIRouter(prefix="/api", tags=["Utilities"])

@router.get("/qr/{vuid}", response_class=Response)
async def get_qr_code_image(vuid: str):
    """
    Genera y devuelve una imagen PNG de un código QR para el VUID proporcionado.
    """
    if not vuid:
        return Response(status_code=400, content="VUID is required.")
        
    # Genera la imagen en memoria
    image_buffer = qr_service.generate_qr_code_in_memory(vuid)
    
    # Devuelve la imagen como una respuesta de streaming
    return Response(content=image_buffer.getvalue(), media_type="image/png")