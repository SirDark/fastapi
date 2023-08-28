from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import FileResponse
import aiofiles
from backgroundTask import BackgroundTask
# for database
import models
from sqlalchemy.orm import Session
import uuid
from databasehandler import get_db

router = APIRouter(
    prefix="",
    tags=["conversion"],
    responses={404: {"description": "not found"}, 500: {"description": "internal server error"}, 200: {"message": "ok"}}
)

convertable_formats = ['.step', '.iges', '.stl', '.obj']


async def savefile(in_file, gen_name):
    async with aiofiles.open("./files/" + gen_name, 'wb') as out_file:
        while content := in_file.file.read(8192):
            await out_file.write(content)


@router.post("/convert")
async def convert(uploadedfile: UploadFile = File(...), convertto: str = Form(...), db: Session = Depends(get_db)):
    if not uploadedfile.filename.lower().endswith(".shapr"):
        raise HTTPException(status_code=400, detail="Only shapr files (.shapr) are allowed.")
    if not (convertto.lower() in convertable_formats):
        raise HTTPException(status_code=400, detail="conversion only supported to " + ' '.join(convertable_formats))
    splitted_filename = uploadedfile.filename.split('.')
    generated_name = splitted_filename[0] + uuid.uuid4().hex + '.' + splitted_filename[-1]

    await savefile(uploadedfile, generated_name)

    conversion_model = models.Conversions()
    conversion_model.original = generated_name
    conversion_model.status = "Waiting"
    conversion_model.converted = (generated_name.split('.'))[0] + convertto
    db.add(conversion_model)
    db.commit()
    conversion_id = conversion_model.id

    backtask = BackgroundTask("./files/" + conversion_model.original, convertto, "./files/", conversion_id)
    backtask.start()
    return conversion_model


@router.get("/history")
async def history(db: Session = Depends(get_db)):
    return db.query(models.Conversions).all()


@router.get("/origin/{file_id}")
async def downloadorigin(file_id: int, db: Session = Depends(get_db)):
    conversion_model = db.query(models.Conversions).filter(models.Conversions.id == file_id).first()
    if conversion_model is None:
        return router.responses.get(404)
    return FileResponse(path='./files/' + conversion_model.original, filename=conversion_model.original,
                        media_type='.shapr')


@router.get("/converted/{file_id}")
async def downloadconverted(file_id: int, db: Session = Depends(get_db)):
    conversion_model = db.query(models.Conversions).filter(models.Conversions.id == file_id).first()
    if conversion_model is None:
        return router.responses.get(404)
    if conversion_model.status != 'Done':
        return {404: {"description": "conversion is still in progress"}}

    fileformat = conversion_model.converted.split('.')[1]
    return FileResponse(path='./files/' + conversion_model.converted, filename=conversion_model.converted,
                        media_type=fileformat)


# only for development purposes will be removed in the future
@router.delete("/deletehistory")
async def deletehistory(db: Session = Depends(get_db)):
    db.query(models.Conversions).delete()
    db.commit()

    return router.responses.get(200)
