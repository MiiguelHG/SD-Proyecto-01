from fastapi import APIRouter, HTTPException
from bson import ObjectId

from DB.db import db
from Schemas.lectorSchema import CreateLector

lector_collection = db["lector"]

router = APIRouter(prefix="/lector", tags=["Lector"])

async def obtenerLector(id: str):
    try:
        lector = await lector_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if lector:
        lector["_id"] = str(lector["_id"])
        return lector
    raise HTTPException(status_code=404, detail="Lector no encontrado")

@router.post("/", response_description="Agregar un lector", status_code=201)
async def saveLector(lector: CreateLector):
    try:
        result = await lector_collection.insert_one(lector.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.acknowledged:
        # Return 201 Created status code y el ID del lector creado
        return await obtenerLector(str(result.inserted_id))
        
    raise HTTPException(status_code=404, detail="Lector no creado")

@router.get("/", response_description="Obtener todos los lectores")
async def getAllLectores():
    lectores_list = []
    try:
        lectores = await lector_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    for lector in lectores:
        lector["_id"] = str(lector["_id"])
        lectores_list.append(lector)
    return lectores_list

@router.get("/{id}", response_description="Obtener un lector por su ID")
async def getLectorById(id: str):
    return await obtenerLector(id)

@router.put("/{id}", response_description="Actualizar un lector por su ID")
async def updateLectorbyId(id: str, lector: CreateLector):
    try:
        result = await lector_collection.update_one({"_id": ObjectId(id)}, {"$set": lector.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.modified_count == 1:
        return await obtenerLector(id)
    raise HTTPException(status_code=404, detail="No se pudo actualizar el lector")

@router.delete("/{id}", response_description="Eliminar un lector por su ID")
async def deleteLector(id: str):
    try:
        result = await lector_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.deleted_count == 1:
        return HTTPException(status_code=204, detail="Lector eliminado exitosamente")
    raise HTTPException(status_code=404, detail="No se pudo eliminar el lector")