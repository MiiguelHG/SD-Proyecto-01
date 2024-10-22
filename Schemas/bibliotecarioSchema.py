from pydantic import BaseModel

class CreateBibliotecario(BaseModel):
    nombre: str
    apellido: str
    correo: str

class Bibliotecario(CreateBibliotecario):
    id: str | None = None

    class Config:
        from_atributes = True