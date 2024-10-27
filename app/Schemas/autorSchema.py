from pydantic import BaseModel

class CreateAutor(BaseModel):
    nombre: str
    apellido: str
    biografia: str