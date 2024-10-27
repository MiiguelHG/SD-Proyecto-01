from pydantic import BaseModel

class CreateLector(BaseModel):
    nombre: str
    apellido: str
    correo: str