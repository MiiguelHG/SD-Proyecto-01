from pydantic import BaseModel

class CreateLibro(BaseModel):
    titulo: str
    autor_id: str
    descripcion: str
    imagen_portada: str
    inventario: bool