from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from bson import ObjectId
import os

from ..DB.db import db
from ..Schemas.libroSchema import CreateLibro
from ..Utils.s3_utils import subir_objeto, eliminar_objeto
import shutil

libro_collection = db["libro"]
autor_collection = db["autor"]

router = APIRouter(prefix="/libro", tags=["Libro"])

async def obtenerLibro(id: str):
    try:
        libro = await libro_collection.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error encotrar libro: {str(e)}")
    
    if libro:
        libro["_id"] = str(libro["_id"])
        libro["autor_id"] = str(libro["autor_id"])
        return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")

# Agregar un libro
@router.post("/", response_description="Agregar un libro", status_code=201)
async def saveLibro(titulo: str = Form(...),
                    autor_id: str = Form(...),
                    descripcion: str = Form(...),
                    inventario: bool = Form(...),
                     imagen_portada: UploadFile = File(...)):
    # Buscar el autor del libro
    try:
        autor = await autor_collection.find_one({"_id": ObjectId(autor_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Buscar: {str(e)}")
    
    # Verificar si el autor existe
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    
    try:
        # Guardar el archivo temporalmente
        with open(imagen_portada.filename, "wb") as buffer:
            shutil.copyfileobj(imagen_portada.file, buffer)
        # Subir la imagen a S3
        imagen_url = subir_objeto(imagen_portada.filename, "Portadas")
        # Eliminar el archivo temporal
        os.remove(imagen_portada.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Guardar archivo: {str(e)}")
    
    # parsear el autor_id a ObjectId, agregar la URL de la imagen y guardar el libro
    try:
        libro = CreateLibro(titulo=titulo, autor_id=autor_id, descripcion=descripcion, imagen_portada=imagen_url, inventario=inventario)
        autor_id = ObjectId(libro.autor_id)
        libro_dict = libro.dict()
        libro_dict["autor_id"] = autor_id
        result = await libro_collection.insert_one(libro_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Insertar MongoDB: {str(e)}")
    
    if result.acknowledged:
        # Return 201 Created status code y el ID del libro creado
        return await obtenerLibro(str(result.inserted_id))
    raise HTTPException(status_code=404, detail="Libro no creado")

# Obtener todos los libros
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

# Obtener un libro por su ID
@router.get("/{id}", response_description="Obtener un libro por su ID")
async def getLibroById(id: str):
    return await obtenerLibro(id)

# Actualizar un libro por su ID
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
    # Eliminar la imagen de la portada
    try:
        libro = await obtenerLibro(id)
        imagen_url = libro["imagen_portada"]
        # Extraer la última parte de la URL
        nombre_archivo = imagen_url.split('/')[-1]
        # Eliminar el archivo del bucket
        eliminar_objeto(nombre_archivo, "Portadas")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminar Img Bucket: {str(e)}")
    
    # Busca y elimina el libro
    try:
        result = await libro_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.deleted_count == 1:
        return HTTPException(status_code=204, detail="Libro eliminado exitosamente")
    raise HTTPException(status_code=404, detail="Libro no eliminado")