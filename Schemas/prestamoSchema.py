from pydantic import BaseModel
from datetime import date

class createPrestamo(BaseModel):
    lector_id: str
    libro_id: str
    fecha_prestamo: date
    fecha_devolucion: date
    bibliotecario_id: str
    foto_credencial: str


