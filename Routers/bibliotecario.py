from fastapi import APIRouter, HTTPException
from bson import ObjectId

from ..DB.db import db
from ..Schemas.bibliotecarioSchema import CreateBibliotecario

Bibliotecario_collection = db["bibliotecario"]

router = APIRouter(prefix="/bibliotecario", tags=["Bibliotecario"])

async def obtenerBibliotecario(id: str):
    try:
        bibliotecario = await Bibliotecario_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if bibliotecario:
        bibliotecario["_id"] = str(bibliotecario["_id"])
        return bibliotecario
    raise HTTPException(status_code=404, detail="Bibliotecario no encontrado")

@router.post("/", response_description="Agregar un bibliotecario", status_code=201)
async def saveBibliotecario(bibliotecario: CreateBibliotecario):
    try:
        result = await Bibliotecario_collection.insert_one(bibliotecario.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.acknowledged:
        # Return 201 Created status code y el ID del bibliotecario creado
        return await obtenerBibliotecario(str(result.inserted_id))
        
    raise HTTPException(status_code=404, detail="Bibliotecario no creado")

@router.get("/", response_description="Obtener todos los bibliotecarios")
async def getAllBibliotecarios():
    bibliotecarios_list = []
    try:
        bibliotecarios = await Bibliotecario_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    for bibliotecario in bibliotecarios:
        bibliotecario["_id"] = str(bibliotecario["_id"])
        bibliotecarios_list.append(bibliotecario)
    return bibliotecarios_list

@router.get("/{id}", response_description="Obtener un bibliotecario por su ID")
async def getBibliotecarioById(id: str):
    return await obtenerBibliotecario(id)

@router.put("/{id}", response_description="Actualizar un bibliotecario por su ID")
async def updateBibliotecariobyId(id: str, bibliotecario: CreateBibliotecario):
    try:
        result = await Bibliotecario_collection.update_one({"_id": ObjectId(id)}, {"$set": bibliotecario.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.modified_count == 1:
        return await obtenerBibliotecario(id)
    raise HTTPException(status_code=404, detail="Bibliotecario no actualizado")

@router.delete("/{id}", response_description="Eliminar un bibliotecario por su ID")
async def deleteBibliotecarioById(id: str):
    try:
        result = await Bibliotecario_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.deleted_count == 1:
        return HTTPException(status_code=204, detail="Bibliotecario eliminado")
    raise HTTPException(status_code=404, detail="Bibliotecario no eliminado")