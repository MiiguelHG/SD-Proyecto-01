from pydantic import BaseModel
from datetime import datetime

class createPrestamo(BaseModel):
    lector_id: str
    libro_id: str
    fecha_prestamo: datetime
    fecha_devolucion: datetime
    bibliotecario_id: str
    foto_credencial: str

class updatePrestamo(BaseModel):
    lector_id: str
    libro_id: str
    bibliotecario_id: str
    foto_credencial: str