from fastapi import APIRouter, HTTPException
from bson import ObjectId

from ..DB.db import db
from ..Schemas.autorSchema import CreateAutor

Autor_collection = db["autor"]

router = APIRouter(prefix="/autor", tags=["Autor"])

async def obtenerAutor(id: str):
    try:
        autor = await Autor_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if autor:
        autor["_id"] = str(autor["_id"])
        return autor
    raise HTTPException(status_code=404, detail="Autor no encontrado")

@router.post("/", response_description="Agregar un autor", status_code=201)
async def saveAutor(autor: CreateAutor):
    try:
        result = await Autor_collection.insert_one(autor.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.acknowledged:
        # Return 201 Created status code y el ID del autor creado
        return await obtenerAutor(str(result.inserted_id))
        
    raise HTTPException(status_code=404, detail="Autor no creado")

@router.get("/", response_description="Obtener todos los autores")
async def getAllAutores():
    autores_list = []
    try:
        autores = await Autor_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    for autor in autores:
        autor["_id"] = str(autor["_id"])
        autores_list.append(autor)
    return autores_list

@router.get("/{id}", response_description="Obtener un autor por su ID")
async def getAutorById(id: str):
    return await obtenerAutor(id)

@router.put("/{id}", response_description="Actualizar un autor por su ID")
async def updateAutorbyId(id: str, autor: CreateAutor):
    try:
        result = await Autor_collection.update_one({"_id": ObjectId(id)}, {"$set": autor.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.modified_count == 1:
        return await obtenerAutor(id)
    raise HTTPException(status_code=404, detail="Autor no actualizado")

@router.delete("/{id}", response_description="Eliminar un autor por su ID")
async def deleteAutorById(id: str):
    try:
        result = await Autor_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.deleted_count == 1:
        return HTTPException(status_code=204, detail="Autor eliminado exitosamente")
    raise HTTPException(status_code=404, detail="Autor no eliminado")