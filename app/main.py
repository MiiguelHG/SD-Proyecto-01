from fastapi import FastAPI
from .Routers import bibliotecario, autor, lector, libro, prestamo

app = FastAPI()

app.include_router(bibliotecario.router)
app.include_router(autor.router)
app.include_router(lector.router)
app.include_router(libro.router)
app.include_router(prestamo.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}