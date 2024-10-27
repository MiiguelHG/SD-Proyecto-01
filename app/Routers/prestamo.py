from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from bson import ObjectId
from datetime import date, timedelta, datetime
import os

from ..DB.db import db
from ..Schemas.prestamoSchema import createPrestamo, updatePrestamo
from ..Utils.s3_utils import subir_objeto, eliminar_objeto
import shutil

prestamo_collection = db["prestamo"]
lector_collection = db["lector"]
libro_collection = db["libro"]
bibliotecario_collection = db["bibliotecario"]

router = APIRouter(prefix="/prestamo", tags=["prestamo"])

async def obtenerPrestamo(id: str):
    try:
        prestamo = await prestamo_collection.find_one({"_id":ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al encontrar prestamo: {str(e)}")
    
    if prestamo:
        prestamo["_id"] = str(prestamo["_id"])
        prestamo["lector_id"] = str(prestamo["lector_id"])
        prestamo["libro_id"] = str(prestamo["libro_id"])
        prestamo["bibliotecario_id"] = str(prestamo["bibliotecario_id"])
        return prestamo
    raise HTTPException(status_code=404, detail="Préstamo no encontrado")

# Agregar un prestamo
@router.post("/", response_description="Agregar un préstamo", status_code=201)
async def savePrestamo(lector_id: str = Form(...), 
                       libro_id: str = Form(...), 
                       bibliotecario_id: str = Form(...),
                       foto_credencial: UploadFile = File(...)):
    
    # Se obtiene la fecha del día y se le suman tres días
    fecha_prestamo = datetime.combine(date.today(), datetime.min.time())
    fecha_devolucion = datetime.combine(date.today() + timedelta(days=3), datetime.min.time())

    try:
        lector = await lector_collection.find_one({"_id": ObjectId(lector_id)})    
        libro = await libro_collection.find_one({"_id": ObjectId(libro_id)})
        bibliotecario = await bibliotecario_collection.find_one({"_id": ObjectId(bibliotecario_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Buscar: {str(e)}")
    
    # Verificar existencia
    if not lector:
        raise HTTPException(status_code=404, detail="Lector no encontrado")
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if not bibliotecario:
        raise HTTPException(status_code=404, detail="Bibliotecario no encontrado")
    
    # Verificar que el esté disponible
    if libro["inventario"] == False:
        raise HTTPException(status_code=200, detail="Libro no disponible")

    try:
        # Guardar el archivo temporalmente
        with open(foto_credencial.filename, "wb") as buffer:
            shutil.copyfileobj(foto_credencial.file, buffer)
        # Subir la imagen a S3
        imagen_url = subir_objeto(foto_credencial.filename, "Credenciales")
        # Eliminar el archivo temporal
        os.remove(foto_credencial.filename)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error Guardar archivo: {str(e)}")
    
    try:
        prestamo = createPrestamo(
            lector_id=lector_id, 
            libro_id=libro_id, 
            fecha_prestamo=fecha_prestamo, 
            fecha_devolucion=fecha_devolucion, 
            bibliotecario_id=bibliotecario_id, 
            foto_credencial=imagen_url
        )
        lector_id = ObjectId(prestamo.lector_id)
        libro_id = ObjectId(prestamo.libro_id)
        bibliotecario_id = ObjectId(prestamo.bibliotecario_id)
        prestamo_dict = prestamo.dict()
        prestamo_dict["lector_id"] = lector_id
        prestamo_dict["libro_id"] = libro_id
        prestamo_dict["bibliotecario_id"] = bibliotecario_id
        result = await prestamo_collection.insert_one(prestamo_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Insertar MongoDB: {str(e)}")
    
    if result.acknowledged:
        # Retorna 201 Created status code y el ID del libro creado
        return await obtenerPrestamo(str(result.inserted_id))
    raise HTTPException(status_code=404, detail="Prestamo no creado")

# Obtener todo los préstamos
@router.get("/", response_description="Obtener todos los libros")
async def getAllPrestamos():
    prestamos_list = []
    try:
        prestamos = await prestamo_collection.find().to_list(None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    for prestamo in prestamos:
        prestamo["_id"] = str(prestamo["_id"])
        prestamo["lector_id"] = str(prestamo["lector_id"])
        prestamo["libro_id"] = str(prestamo["libro_id"])
        prestamo["bibliotecario_id"] = str(prestamo["bibliotecario_id"])
        prestamos_list.append(prestamo)
    return prestamos_list

# Obtener un prestamo por su ID
@router.get("/{id}", response_description="Obtener un préstamo por su ID")
async def getPrestamoById(id: str):
    return await obtenerPrestamo(id)

# Actualizar un prestamo por su ID
@router.put("/{id}", response_description="Actualizar un libro por su ID")
async def updatePrestamoById(id: str, prestamo: updatePrestamo):
    # Verificar que el prestamo exista
    try:
        res = await prestamo_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error buscar prestamo: {str(e)}")
    
    if not res:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    try:
        lector = await lector_collection.find_one({"_id": ObjectId(prestamo.lector_id)})    
        libro = await libro_collection.find_one({"_id": ObjectId(prestamo.libro_id)})
        bibliotecario = await bibliotecario_collection.find_one({"_id": ObjectId(prestamo.bibliotecario_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Buscar: {str(e)}")
    
    # Verificar existencia
    if not lector:
        raise HTTPException(status_code=404, detail="Lector no encontrado")
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if not bibliotecario:
        raise HTTPException(status_code=404, detail="Bibliotecario no encontrado")
    
    try:
        lector_id = ObjectId(prestamo.lector_id)
        libro_id = ObjectId(prestamo.libro_id)
        bibliotecario_id = ObjectId(prestamo.bibliotecario_id)
        prestamo_dict = prestamo.dict()
        prestamo_dict["lector_id"] = lector_id
        prestamo_dict["libro_id"] = libro_id
        prestamo_dict["bibliotecario_id"] = bibliotecario_id
        prestamo_dict["fecha_prestamo"] = datetime.combine(date.today(), datetime.min.time())
        prestamo_dict["fecha_devolucion"] = datetime.combine(date.today() + timedelta(days=3), datetime.min.time())
        result = await prestamo_collection.update_one({"_id": ObjectId(id)}, {"$set":prestamo_dict})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error actualizar: {str(e)}")
    
    if result.modified_count == 1:
        return await obtenerPrestamo(id)
    raise HTTPException(status_code=404, detail="Prestamo no actualizado")

@router.delete("/{id}", response_description="Eliminar un préstamo por su ID") 
async def deletePrestamo(id: str):
    try:
        prestamo = await obtenerPrestamo(id)
        imagen_url = prestamo["foto_credencial"]
        nombre_archivo = imagen_url.split('/')[-1]
        eliminar_objeto(nombre_archivo, "Credenciales")      
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminar Img Bucket: {str(e)}")
    
    try:
        result = await prestamo_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminar: {str(e)}")
    
    if result.deleted_count == 1:
        return HTTPException(status_code=204, detail="Préstamo eliminado exitosamente")
    raise HTTPException(status_code=404, detail="Préstamo no eliminado")
