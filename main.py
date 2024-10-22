from fastapi import FastAPI
from Routers import bibliotecario, autor, lector, libro

app = FastAPI()

app.include_router(bibliotecario.router)
app.include_router(autor.router)
app.include_router(lector.router)
app.include_router(libro.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}