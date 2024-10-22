from fastapi import APIRouter, HTTPException
from bson import ObjectId

from DB.db import db
from Schemas.libroSchema import CreateLibro

libro_collection = db["libro"]
autor_collection = db["autor"]

router = APIRouter(prefix="/libro", tags=["Libro"])

async def obtenerLibro(id: str):
    try:
        libro = await libro_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if libro:
        libro["_id"] = str(libro["_id"])
        libro["autor_id"] = str(libro["autor_id"])
        return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@router.post("/", response_description="Agregar un libro", status_code=201)
async def saveLibro(libro: CreateLibro):
    try:
        autor = await autor_collection.find_one({"_id": ObjectId(libro.autor_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    
    try:
        autor_id = ObjectId(libro.autor_id)
        libro_dict = libro.dict()
        libro_dict["autor_id"] = autor_id
        result = await libro_collection.insert_one(libro_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.acknowledged:
        # Return 201 Created status code y el ID del libro creado
        return await obtenerLibro(str(result.inserted_id))
    raise HTTPException(status_code=404, detail="Libro no creado")

@router.get("/", response_description="Obtener todos los libros")
async def getAllLibros():
    libros_list = []
    try:
        libros = await libro_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    for libro in libros:
        libro["_id"] = str(libro["_id"])
        libro["autor_id"] = str(libro["autor_id"])
        libros_list.append(libro)
    return libros_list

@router.get("/{id}", response_description="Obtener un libro por su ID")
async def getLibroById(id: str):
    return await obtenerLibro(id)

@router.put("/{id}", response_description="Actualizar un libro por su ID")
async def updateLibrobyId(id: str, libro: CreateLibro):
    try:
        autor = await autor_collection.find_one({"_id": ObjectId(libro.autor_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    
    try:
        autor_id = ObjectId(libro.autor_id)
        libro_dict = libro.dict()
        libro_dict["autor_id"] = autor_id
        result = await libro_collection.update_one({"_id": ObjectId(id)}, {"$set": libro_dict})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.modified_count == 1:
        return await obtenerLibro(id)
    raise HTTPException(status_code=404, detail="Libro no actualizado")

@router.delete("/{id}", response_description="Eliminar un libro por su ID")
async def deleteLibro(id: str):
    try:
        result = await libro_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.deleted_count == 1:
        HTTPException(status_code=204, detail="Libro eliminado exitosamente")
    raise HTTPException(status_code=404, detail="Libro no eliminado")